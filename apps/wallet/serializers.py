from decimal import Decimal

from rest_framework import serializers

from apps.wallet.models import Wallet, Transaction


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance_cop', 'balance_llo', 'is_active', 'created_at']
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display', read_only=True,
    )
    currency_display = serializers.CharField(
        source='get_currency_display', read_only=True,
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )

    class Meta:
        model = Transaction
        fields = [
            'id',
            'wallet',
            'transaction_type',
            'transaction_type_display',
            'amount',
            'currency',
            'currency_display',
            'balance_after',
            'reference',
            'description',
            'metadata',
            'status',
            'status_display',
            'created_at',
        ]
        read_only_fields = fields


class TransactionFilterSerializer(serializers.Serializer):
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    transaction_type = serializers.ChoiceField(
        choices=Transaction.TransactionType.choices,
        required=False,
    )
    currency = serializers.ChoiceField(
        choices=Transaction.Currency.choices,
        required=False,
    )


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )
    currency = serializers.ChoiceField(choices=Transaction.Currency.choices)


class BalanceSummarySerializer(serializers.Serializer):
    balance_cop = serializers.DecimalField(max_digits=15, decimal_places=2)
    balance_llo = serializers.DecimalField(max_digits=15, decimal_places=2)
    llo_cop_equivalent = serializers.DecimalField(max_digits=15, decimal_places=2)
