from rest_framework import serializers

from apps.notifications.models import Notification, DeviceToken


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', read_only=True,
    )
    channel_display = serializers.CharField(
        source='get_channel_display', read_only=True,
    )

    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'notification_type_display',
            'title',
            'message',
            'data',
            'channel',
            'channel_display',
            'is_read',
            'is_sent',
            'sent_at',
            'read_at',
            'created_at',
        ]
        read_only_fields = fields


class NotificationMarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text='Lista de IDs de notificaciones a marcar como leidas.',
    )


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['id', 'token', 'platform', 'is_active', 'created_at']
        read_only_fields = ['id', 'is_active', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        device_token, created = DeviceToken.objects.update_or_create(
            user=user,
            token=validated_data['token'],
            defaults={
                'platform': validated_data['platform'],
                'is_active': True,
            },
        )
        return device_token


class NotificationPreferenceSerializer(serializers.Serializer):
    push_enabled = serializers.BooleanField(default=True)
    sms_enabled = serializers.BooleanField(default=True)
    email_enabled = serializers.BooleanField(default=False)
    quiet_hours_start = serializers.TimeField(required=False, allow_null=True)
    quiet_hours_end = serializers.TimeField(required=False, allow_null=True)
