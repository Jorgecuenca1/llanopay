from decimal import Decimal

from django.conf import settings
from rest_framework import serializers

from apps.accounts.models import User
from apps.transfers.models import Transfer, TransferLimit, ScheduledTransfer


# ---- Nested serializers ----

class UserBriefSerializer(serializers.ModelSerializer):
    """Representacion breve del usuario para transferencias."""
    phone_number = serializers.CharField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name']
        read_only_fields = fields


# ---- Transfer serializers ----

class TransferCreateSerializer(serializers.Serializer):
    """Serializer para iniciar una transferencia P2P."""
    receiver_phone = serializers.CharField(
        max_length=20,
        help_text='Numero de telefono del destinatario (ej. +573001234567)',
    )
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('0.01'),
        help_text='Monto a transferir',
    )
    currency = serializers.ChoiceField(
        choices=Transfer.Currency.choices,
        default=Transfer.Currency.COP,
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        max_length=500,
    )

    def validate_receiver_phone(self, value):
        """Verifica que el destinatario exista y tenga billetera activa."""
        try:
            receiver = User.objects.get(phone_number=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'No se encontro un usuario con ese numero de telefono.',
            )

        if not receiver.is_verified:
            raise serializers.ValidationError(
                'El destinatario no ha verificado su cuenta.',
            )

        if not hasattr(receiver, 'wallet') or not receiver.wallet.is_active:
            raise serializers.ValidationError(
                'El destinatario no tiene una billetera activa.',
            )

        return value

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError('Se requiere autenticacion.')

        sender = request.user

        # No transferir a si mismo
        if str(sender.phone_number) == attrs['receiver_phone']:
            raise serializers.ValidationError(
                {'receiver_phone': 'No puedes transferir a tu propia cuenta.'},
            )

        # Verificar billetera del remitente
        if not hasattr(sender, 'wallet') or not sender.wallet.is_active:
            raise serializers.ValidationError(
                'Tu billetera no esta activa.',
            )

        # Verificar limites
        limit, _created = TransferLimit.objects.get_or_create(user=sender)
        ok, msg = limit.check_all_limits(attrs['amount'], attrs['currency'])
        if not ok:
            raise serializers.ValidationError({'amount': msg})

        # Verificar saldo suficiente (monto + comision estimada)
        commission_rate = Transfer.calculate_commission_rate(
            attrs['amount'], attrs['currency'],
        )
        estimated_commission = (attrs['amount'] * commission_rate).quantize(Decimal('0.01'))
        total_needed = attrs['amount'] + estimated_commission

        if attrs['currency'] == Transfer.Currency.COP:
            if sender.wallet.balance_cop < total_needed:
                raise serializers.ValidationError({
                    'amount': (
                        f'Saldo COP insuficiente. '
                        f'Se requiere {total_needed} (incluye comision de {estimated_commission}), '
                        f'disponible {sender.wallet.balance_cop}.'
                    ),
                })
        else:
            if sender.wallet.balance_llo < total_needed:
                raise serializers.ValidationError({
                    'amount': (
                        f'Saldo LLO insuficiente. '
                        f'Se requiere {total_needed} (incluye comision de {estimated_commission}), '
                        f'disponible {sender.wallet.balance_llo}.'
                    ),
                })

        return attrs


class TransferDetailSerializer(serializers.ModelSerializer):
    """Serializer completo de una transferencia con datos del remitente y destinatario."""
    sender = UserBriefSerializer(read_only=True)
    receiver = UserBriefSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)

    class Meta:
        model = Transfer
        fields = [
            'id',
            'sender',
            'receiver',
            'amount',
            'currency',
            'currency_display',
            'commission_amount',
            'commission_rate',
            'description',
            'reference',
            'status',
            'status_display',
            'otp_verified',
            'created_at',
            'completed_at',
        ]
        read_only_fields = fields


class TransferConfirmSerializer(serializers.Serializer):
    """Serializer para confirmar una transferencia con OTP."""
    transfer_id = serializers.UUIDField(
        help_text='ID de la transferencia a confirmar',
    )
    otp_code = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text='Codigo OTP de 6 digitos',
    )

    def validate_transfer_id(self, value):
        request = self.context.get('request')
        try:
            transfer = Transfer.objects.get(pk=value, sender=request.user)
        except Transfer.DoesNotExist:
            raise serializers.ValidationError(
                'No se encontro la transferencia.',
            )

        if transfer.status != Transfer.Status.OTP_REQUIRED:
            raise serializers.ValidationError(
                'Esta transferencia no requiere confirmacion OTP.',
            )

        return value

    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('El codigo OTP debe ser numerico.')
        return value


# ---- Limit serializers ----

class TransferLimitSerializer(serializers.ModelSerializer):
    """Serializer para los limites de transferencia del usuario."""

    class Meta:
        model = TransferLimit
        fields = [
            'daily_limit_cop',
            'monthly_limit_cop',
            'per_transaction_limit_cop',
        ]


# ---- Scheduled transfer serializers ----

class ScheduledTransferSerializer(serializers.ModelSerializer):
    """Serializer para transferencias programadas."""
    sender = UserBriefSerializer(read_only=True)
    receiver = UserBriefSerializer(read_only=True)
    receiver_phone = serializers.CharField(write_only=True, required=False)
    frequency_display = serializers.CharField(
        source='get_frequency_display', read_only=True,
    )

    class Meta:
        model = ScheduledTransfer
        fields = [
            'id',
            'sender',
            'receiver',
            'receiver_phone',
            'amount',
            'currency',
            'frequency',
            'frequency_display',
            'next_execution_date',
            'is_active',
            'description',
            'created_at',
        ]
        read_only_fields = ['id', 'sender', 'receiver', 'created_at']

    def validate_receiver_phone(self, value):
        try:
            User.objects.get(phone_number=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'No se encontro un usuario con ese numero de telefono.',
            )
        return value

    def validate_amount(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError('El monto debe ser positivo.')
        return value

    def create(self, validated_data):
        receiver_phone = validated_data.pop('receiver_phone')
        receiver = User.objects.get(phone_number=receiver_phone)
        validated_data['sender'] = self.context['request'].user
        validated_data['receiver'] = receiver
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'receiver_phone' in validated_data:
            receiver_phone = validated_data.pop('receiver_phone')
            receiver = User.objects.get(phone_number=receiver_phone)
            validated_data['receiver'] = receiver
        return super().update(instance, validated_data)
