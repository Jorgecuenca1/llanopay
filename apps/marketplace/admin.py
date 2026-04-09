from django.contrib import admin

from .models import (
    Merchant,
    MerchantCategory,
    MerchantPayment,
    MerchantReview,
    Promotion,
)


@admin.register(MerchantCategory)
class MerchantCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = [
        'business_name',
        'category',
        'city',
        'department',
        'is_verified',
        'is_active',
        'rating',
        'total_sales',
        'created_at',
    ]
    list_filter = ['department', 'category', 'is_verified', 'is_active']
    search_fields = ['business_name', 'user__first_name', 'user__last_name', 'city']
    prepopulated_fields = {'slug': ('business_name',)}
    readonly_fields = ['rating', 'total_reviews', 'total_sales', 'created_at', 'updated_at']
    list_editable = ['is_verified', 'is_active']
    raw_id_fields = ['user', 'category']


@admin.register(MerchantPayment)
class MerchantPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'reference',
        'merchant',
        'payer',
        'amount',
        'currency',
        'commission_amount',
        'status',
        'created_at',
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['reference', 'merchant__business_name', 'payer__first_name']
    readonly_fields = ['reference', 'created_at', 'completed_at']
    raw_id_fields = ['merchant', 'payer']


@admin.register(MerchantReview)
class MerchantReviewAdmin(admin.ModelAdmin):
    list_display = ['merchant', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['merchant__business_name', 'user__first_name', 'comment']
    readonly_fields = ['created_at']
    raw_id_fields = ['merchant', 'user']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'merchant',
        'discount_percentage',
        'discount_amount',
        'start_date',
        'end_date',
        'is_active',
    ]
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'merchant__business_name']
    list_editable = ['is_active']
    raw_id_fields = ['merchant']
