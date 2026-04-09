from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import KYCDocument, OTPCode, User


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = [
            'phone_number',
            'document_type',
            'document_number',
            'first_name',
            'last_name',
            'password',
        ]

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                'Ya existe un usuario registrado con este numero de telefono.'
            )
        return value

    def validate_document_number(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                'El numero de documento no puede estar vacio.'
            )
        return value.strip()

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            document_type=validated_data['document_type'],
            document_number=validated_data['document_number'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        # Create OTP for registration verification
        OTPCode.objects.create(
            user=user,
            purpose=OTPCode.Purpose.REGISTER,
        )
        return user


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for OTP verification."""

    phone_number = serializers.CharField()
    code = serializers.CharField(max_length=6, min_length=6)
    purpose = serializers.ChoiceField(choices=OTPCode.Purpose.choices)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        code = attrs.get('code')
        purpose = attrs.get('purpose')

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'phone_number': 'No se encontro un usuario con este numero de telefono.'}
            )

        otp = OTPCode.objects.filter(
            user=user,
            code=code,
            purpose=purpose,
            is_used=False,
        ).order_by('-created_at').first()

        if otp is None:
            raise serializers.ValidationError(
                {'code': 'Codigo OTP invalido.'}
            )

        if otp.is_expired:
            raise serializers.ValidationError(
                {'code': 'El codigo OTP ha expirado.'}
            )

        attrs['user'] = user
        attrs['otp'] = otp
        return attrs


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    phone_number = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            phone_number=phone_number,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                'Credenciales invalidas. Verifique su numero de telefono y contrasena.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'Esta cuenta ha sido desactivada.'
            )

        if not user.is_verified:
            raise serializers.ValidationError(
                'Debe verificar su numero de telefono antes de iniciar sesion.'
            )

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for reading and updating user profile."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id',
            'phone_number',
            'document_type',
            'document_number',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'is_verified',
            'is_merchant',
            'profile_picture',
            'date_of_birth',
            'city',
            'department',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'phone_number',
            'document_type',
            'document_number',
            'is_verified',
            'is_merchant',
            'created_at',
            'updated_at',
        ]


class KYCDocumentSerializer(serializers.ModelSerializer):
    """Serializer for KYC document management."""

    class Meta:
        model = KYCDocument
        fields = [
            'id',
            'user',
            'document_type',
            'front_image',
            'back_image',
            'selfie_image',
            'status',
            'reviewed_at',
            'reviewer_notes',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'reviewed_at',
            'reviewer_notes',
            'created_at',
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""

    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
        style={'input_type': 'password'},
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'La contrasena actual es incorrecta.'
            )
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user
