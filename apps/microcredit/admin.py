from django.contrib import admin

from apps.microcredit.models import (
    CreditProfile,
    Microcredit,
    MicrocreditPayment,
    MicrocreditProduct,
)


@admin.register(CreditProfile)
class CreditProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'credit_score',
        'max_credit_amount',
        'total_loans',
        'active_loans',
        'on_time_payments',
        'late_payments',
        'last_evaluated_at',
    ]
    list_filter = ['credit_score', 'active_loans']
    search_fields = [
        'user__phone_number',
        'user__first_name',
        'user__last_name',
        'user__document_number',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'last_evaluated_at',
    ]


@admin.register(MicrocreditProduct)
class MicrocreditProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'min_amount',
        'max_amount',
        'interest_rate_monthly',
        'term_days',
        'grace_period_days',
        'requires_llo_collateral',
        'is_active',
    ]
    list_filter = ['is_active', 'requires_llo_collateral']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


class MicrocreditPaymentInline(admin.TabularInline):
    model = MicrocreditPayment
    extra = 0
    readonly_fields = ['id', 'amount', 'payment_type', 'status', 'created_at', 'completed_at']
    can_delete = False


@admin.register(Microcredit)
class MicrocreditAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'product',
        'amount_requested',
        'amount_approved',
        'total_to_repay',
        'amount_repaid',
        'status',
        'due_date',
        'created_at',
    ]
    list_filter = ['status', 'product', 'created_at']
    search_fields = [
        'user__phone_number',
        'user__first_name',
        'user__last_name',
        'user__document_number',
    ]
    readonly_fields = ['id', 'created_at']
    inlines = [MicrocreditPaymentInline]
    date_hierarchy = 'created_at'


@admin.register(MicrocreditPayment)
class MicrocreditPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'microcredit',
        'amount',
        'payment_type',
        'status',
        'created_at',
        'completed_at',
    ]
    list_filter = ['payment_type', 'status', 'created_at']
    search_fields = [
        'microcredit__user__phone_number',
        'microcredit__user__first_name',
    ]
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
