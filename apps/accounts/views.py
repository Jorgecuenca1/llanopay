from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import KYCDocument, OTPCode, User
from .serializers import (
    ChangePasswordSerializer,
    KYCDocumentSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    VerifyOTPSerializer,
)


class RegisterView(generics.CreateAPIView):
    """Register a new user and send OTP for verification."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Retrieve the OTP created during registration
        otp = user.otp_codes.filter(
            purpose=OTPCode.Purpose.REGISTER,
            is_used=False,
        ).first()

        return Response(
            {
                'message': 'Usuario registrado exitosamente. Se ha enviado un codigo OTP.',
                'phone_number': str(user.phone_number),
                'otp_purpose': OTPCode.Purpose.REGISTER,
                # Include OTP in response only for development/testing
                'otp_code': otp.code if otp else None,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(APIView):
    """Verify an OTP code."""

    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        otp = serializer.validated_data['otp']
        purpose = serializer.validated_data['purpose']

        # Mark OTP as used
        otp.is_used = True
        otp.save(update_fields=['is_used'])

        # If the purpose is REGISTER, verify the user
        if purpose == OTPCode.Purpose.REGISTER:
            user.is_verified = True
            user.save(update_fields=['is_verified'])

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'message': 'Codigo OTP verificado exitosamente.',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    """Authenticate user and return JWT tokens."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'message': 'Inicio de sesion exitoso.',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve and update the authenticated user's profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class KYCDocumentViewSet(viewsets.ModelViewSet):
    """CRUD operations for KYC documents."""

    serializer_class = KYCDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return KYCDocument.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RequestOTPView(APIView):
    """Request a new OTP code for the given phone number and purpose."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        purpose = request.data.get('purpose')

        if not phone_number or not purpose:
            return Response(
                {'error': 'Se requiere el numero de telefono y el proposito.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if purpose not in dict(OTPCode.Purpose.choices):
            return Response(
                {'error': 'Proposito invalido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {'error': 'No se encontro un usuario con este numero de telefono.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Invalidate previous unused OTPs of the same purpose
        OTPCode.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False,
        ).update(is_used=True)

        # Create new OTP
        otp = OTPCode.objects.create(user=user, purpose=purpose)

        return Response(
            {
                'message': 'Codigo OTP enviado exitosamente.',
                'phone_number': str(user.phone_number),
                # Include OTP in response only for development/testing
                'otp_code': otp.code,
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    """Change the authenticated user's password."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'message': 'Contrasena actualizada exitosamente.'},
            status=status.HTTP_200_OK,
        )
