from django.contrib import admin

from apps.notifications.models import Notification, DeviceToken, SMSMessage


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'notification_type', 'channel',
        'is_read', 'is_sent', 'created_at',
    ]
    list_filter = ['notification_type', 'channel', 'is_read', 'is_sent', 'created_at']
    search_fields = ['title', 'message', 'user__phone_number', 'user__first_name']
    readonly_fields = ['id', 'created_at', 'sent_at', 'read_at']
    raw_id_fields = ['user']


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'is_active', 'created_at', 'updated_at']
    list_filter = ['platform', 'is_active']
    search_fields = ['user__phone_number', 'token']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user']


@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'status', 'cost', 'created_at', 'sent_at']
    list_filter = ['status', 'created_at']
    search_fields = ['phone_number', 'message', 'provider_message_id']
    readonly_fields = ['id', 'created_at']
