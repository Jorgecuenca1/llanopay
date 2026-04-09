from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import KYCDocument, OTPCode, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'phone_number',
        'first_name',
        'last_name',
        'document_type',
        'document_number',
        'is_verified',
        'is_merchant',
        'is_active',
        'created_at',
    ]
    list_filter = [
        'is_verified',
        'is_merchant',
        'is_active',
        'is_staff',
        'document_type',
        'department',
    ]
    search_fields = [
        'phone_number',
        'first_name',
        'last_name',
        'document_number',
        'email',
    ]
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (
            'Informacion personal',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'document_type',
                    'document_number',
                    'date_of_birth',
                    'profile_picture',
                )
            },
        ),
        (
            'Ubicacion',
            {'fields': ('city', 'department')},
        ),
        (
            'Permisos',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'is_verified',
                    'is_merchant',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (
            'Fechas importantes',
            {'fields': ('last_login', 'date_joined')},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'phone_number',
                    'document_type',
                    'document_number',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2',
                ),
            },
        ),
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'code',
        'purpose',
        'is_used',
        'created_at',
        'expires_at',
    ]
    list_filter = ['purpose', 'is_used', 'created_at']
    search_fields = ['user__phone_number', 'code']
    readonly_fields = ['code', 'created_at']
    ordering = ['-created_at']


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'document_type',
        'status',
        'created_at',
        'reviewed_at',
    ]
    list_filter = ['status', 'document_type', 'created_at']
    search_fields = ['user__phone_number', 'user__document_number']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
