from decimal import Decimal

from django.conf import settings
from rest_framework import serializers

from apps.crypto.models import (
    CryptoDeposit,
    CryptoWithdrawal,
    ExchangeRate,
    LlanocoinTransaction,
)


class CryptoDepositSerializer(serializers.ModelSerializer):
    """Serializer para crear un deposito crypto (el usuario envia tx_hash)."""

    class Meta:
        model = CryptoDeposit
        fields = ['currency', 'amount', 'tx_hash', 'network']

    def validate_tx_hash(self, value):
        if CryptoDeposit.objects.filter(tx_hash=value).exists():
            raise serializers.ValidationError(
                "Esta transaccion ya fue registrada."
            )
        return value

    def validate_amount(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "El monto debe ser mayor a cero."
            )
        return value

    def validate(self, attrs):
        currency = attrs.get('currency')
        network = attrs.get('network')

        valid_networks = {
            'USDT': ['POLYGON', 'ETHEREUM', 'BSC'],
            'ETH': ['ETHEREUM', 'POLYGON'],
            'BTC': ['BITCOIN'],
        }

        if network not in valid_networks.get(currency, []):
            raise serializers.ValidationError({
                'network': f"La red {network} no es valida para {currency}."
            })

        return attrs


class CryptoDepositDetailSerializer(serializers.ModelSerializer):
    """Serializer de solo lectura con todos los campos del deposito."""

    user = serializers.StringRelatedField()

    class Meta:
        model = CryptoDeposit
        fields = [
            'id', 'user', 'currency', 'amount', 'tx_hash', 'network',
            'cop_amount', 'exchange_rate', 'status', 'confirmations',
            'required_confirmations', 'created_at', 'confirmed_at',
            'credited_at',
        ]
        read_only_fields = fields


class CryptoWithdrawalSerializer(serializers.ModelSerializer):
    """Serializer para solicitar un retiro crypto."""

    class Meta:
        model = CryptoWithdrawal
        fields = [
            'id', 'currency', 'amount', 'destination_address', 'network',
            'cop_amount', 'exchange_rate', 'fee_amount', 'status',
            'tx_hash', 'created_at', 'processed_at',
        ]
        read_only_fields = [
            'id', 'cop_amount', 'exchange_rate', 'fee_amount', 'status',
            'tx_hash', 'created_at', 'processed_at',
        ]

    def validate_amount(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "El monto debe ser mayor a cero."
            )
        return value

    def validate_destination_address(self, value):
        if not value or len(value) < 10:
            raise serializers.ValidationError(
                "Direccion de destino invalida."
            )
        return value

    def validate(self, attrs):
        currency = attrs.get('currency')
        network = attrs.get('network')

        valid_networks = {
            'USDT': ['POLYGON', 'ETHEREUM', 'BSC'],
            'ETH': ['ETHEREUM', 'POLYGON'],
            'BTC': ['BITCOIN'],
        }

        if network not in valid_networks.get(currency, []):
            raise serializers.ValidationError({
                'network': f"La red {network} no es valida para {currency}."
            })

        return attrs


class ExchangeRateSerializer(serializers.ModelSerializer):
    """Serializer de solo lectura para tasas de cambio."""

    class Meta:
        model = ExchangeRate
        fields = ['currency', 'rate_cop', 'source', 'updated_at']
        read_only_fields = fields


class LlanocoinBuySerializer(serializers.Serializer):
    """Serializer para comprar Llanocoin con saldo COP."""

    amount_cop = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        min_value=Decimal('100'),
    )

    def validate_amount_cop(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "El monto COP debe ser mayor a cero."
            )
        return value


class LlanocoinSellSerializer(serializers.Serializer):
    """Serializer para vender Llanocoin por saldo COP."""

    amount_llo = serializers.DecimalField(
        max_digits=18,
        decimal_places=8,
        min_value=Decimal('0.00000001'),
    )

    def validate_amount_llo(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "La cantidad LLO debe ser mayor a cero."
            )
        return value


class LlanocoinTransactionSerializer(serializers.ModelSerializer):
    """Serializer de solo lectura para transacciones Llanocoin."""

    user = serializers.StringRelatedField()

    class Meta:
        model = LlanocoinTransaction
        fields = [
            'id', 'user', 'transaction_type', 'amount_llo', 'amount_cop',
            'rate', 'status', 'tx_hash', 'created_at',
        ]
        read_only_fields = fields
