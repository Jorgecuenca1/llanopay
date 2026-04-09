from django.contrib import admin

from apps.wallet.models import Wallet, Transaction, MasterWallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance_cop', 'balance_llo', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'wallet', 'transaction_type', 'amount',
        'currency', 'status', 'created_at',
    ]
    list_filter = ['transaction_type', 'currency', 'status', 'created_at']
    search_fields = ['reference', 'wallet__user__email']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['wallet']


@admin.register(MasterWallet)
class MasterWalletAdmin(admin.ModelAdmin):
    list_display = ['balance_cop', 'balance_llo', 'total_crypto_reserves_usd', 'updated_at']
    readonly_fields = ['updated_at']

    def has_add_permission(self, request):
        # Solo permitir un registro (singleton)
        return not MasterWallet.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
