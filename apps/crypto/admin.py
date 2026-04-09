from django.contrib import admin

from apps.crypto.models import (
    CryptoDeposit,
    CryptoWithdrawal,
    ExchangeRate,
    LlanocoinTransaction,
)


@admin.register(CryptoDeposit)
class CryptoDepositAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'currency', 'amount', 'network',
        'cop_amount', 'status', 'confirmations', 'created_at',
    ]
    list_filter = ['status', 'currency', 'network', 'created_at']
    search_fields = ['user__email', 'tx_hash']
    readonly_fields = [
        'tx_hash', 'confirmations', 'exchange_rate', 'cop_amount',
        'created_at', 'confirmed_at', 'credited_at',
    ]
    date_hierarchy = 'created_at'


@admin.register(CryptoWithdrawal)
class CryptoWithdrawalAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'currency', 'amount', 'destination_address',
        'network', 'cop_amount', 'fee_amount', 'status', 'created_at',
    ]
    list_filter = ['status', 'currency', 'network', 'created_at']
    search_fields = ['user__email', 'tx_hash', 'destination_address']
    readonly_fields = [
        'exchange_rate', 'cop_amount', 'fee_amount',
        'created_at', 'processed_at',
    ]
    date_hierarchy = 'created_at'


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['currency', 'rate_cop', 'source', 'updated_at']
    list_filter = ['currency', 'source']
    readonly_fields = ['updated_at']


@admin.register(LlanocoinTransaction)
class LlanocoinTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'transaction_type', 'amount_llo',
        'amount_cop', 'rate', 'status', 'created_at',
    ]
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['user__email', 'tx_hash']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
