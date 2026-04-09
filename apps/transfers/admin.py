from django.contrib import admin

from apps.transfers.models import Transfer, TransferLimit, ScheduledTransfer


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = [
        'reference',
        'sender',
        'receiver',
        'amount',
        'currency',
        'commission_amount',
        'status',
        'created_at',
        'completed_at',
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = [
        'reference',
        'sender__phone_number',
        'sender__first_name',
        'receiver__phone_number',
        'receiver__first_name',
    ]
    readonly_fields = [
        'id',
        'reference',
        'commission_amount',
        'commission_rate',
        'otp_verified',
        'created_at',
        'completed_at',
    ]
    list_select_related = ['sender', 'receiver']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(TransferLimit)
class TransferLimitAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'daily_limit_cop',
        'monthly_limit_cop',
        'per_transaction_limit_cop',
    ]
    search_fields = [
        'user__phone_number',
        'user__first_name',
        'user__last_name',
    ]
    list_select_related = ['user']


@admin.register(ScheduledTransfer)
class ScheduledTransferAdmin(admin.ModelAdmin):
    list_display = [
        'sender',
        'receiver',
        'amount',
        'currency',
        'frequency',
        'next_execution_date',
        'is_active',
        'created_at',
    ]
    list_filter = ['frequency', 'is_active', 'currency']
    search_fields = [
        'sender__phone_number',
        'receiver__phone_number',
    ]
    readonly_fields = ['id', 'created_at']
    list_select_related = ['sender', 'receiver']
    date_hierarchy = 'next_execution_date'
