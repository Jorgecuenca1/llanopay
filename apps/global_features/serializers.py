"""Serializers for global features."""
from rest_framework import serializers

from apps.global_features.models import (
    Country, Currency, MultiBalance, QRPayment, MobileTopup, BillPayment,
    ReferralCode, Referral, VirtualCard, RewardPoints, RewardTransaction,
    WalletTopup,
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class MultiBalanceSerializer(serializers.ModelSerializer):
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)

    class Meta:
        model = MultiBalance
        fields = ['id', 'currency', 'currency_code', 'currency_symbol', 'balance', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class QRPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRPayment
        fields = ['id', 'code', 'receiver', 'payer', 'amount', 'currency',
                  'description', 'status', 'expires_at', 'created_at', 'paid_at']
        read_only_fields = ['id', 'code', 'receiver', 'payer', 'status', 'created_at', 'paid_at']


class MobileTopupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileTopup
        fields = ['id', 'phone_number', 'country_code', 'operator', 'amount', 'currency',
                  'status', 'reference', 'created_at', 'completed_at']
        read_only_fields = ['id', 'status', 'reference', 'created_at', 'completed_at']


class BillPaymentSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = BillPayment
        fields = ['id', 'category', 'category_display', 'company', 'account_number',
                  'amount', 'currency', 'status', 'reference', 'description',
                  'created_at', 'completed_at']
        read_only_fields = ['id', 'status', 'reference', 'created_at', 'completed_at']


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = ['code', 'total_referrals', 'total_earned', 'created_at']


class ReferralSerializer(serializers.ModelSerializer):
    referrer_name = serializers.SerializerMethodField()
    referred_name = serializers.SerializerMethodField()

    class Meta:
        model = Referral
        fields = ['id', 'referrer', 'referrer_name', 'referred', 'referred_name',
                  'bonus_amount', 'bonus_currency', 'bonus_paid', 'created_at']

    def get_referrer_name(self, obj):
        return f'{obj.referrer.first_name} {obj.referrer.last_name}'.strip()

    def get_referred_name(self, obj):
        return f'{obj.referred.first_name} {obj.referred.last_name}'.strip()


class VirtualCardSerializer(serializers.ModelSerializer):
    masked_number = serializers.ReadOnlyField()
    card_holder_name = serializers.CharField(required=False)
    expiry_month = serializers.IntegerField(required=False)
    expiry_year = serializers.IntegerField(required=False)

    class Meta:
        model = VirtualCard
        fields = ['id', 'card_number', 'masked_number', 'card_holder_name',
                  'expiry_month', 'expiry_year', 'cvv', 'card_type', 'status',
                  'currency', 'spending_limit', 'created_at']
        read_only_fields = ['id', 'card_number', 'cvv', 'status', 'created_at']


class RewardPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardPoints
        fields = ['balance', 'lifetime_earned', 'lifetime_redeemed', 'tier', 'updated_at']


class RewardTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardTransaction
        fields = ['id', 'points', 'transaction_type', 'reason', 'created_at']


class WalletTopupSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(source='get_method_display', read_only=True)

    class Meta:
        model = WalletTopup
        fields = ['id', 'amount', 'currency', 'method', 'method_display', 'status',
                  'fee', 'reference', 'description', 'created_at', 'completed_at']
        read_only_fields = ['id', 'status', 'fee', 'reference', 'created_at', 'completed_at']
