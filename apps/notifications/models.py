import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    """Notificacion enviada a un usuario por distintos canales."""

    class NotificationType(models.TextChoices):
        TRANSFER_RECEIVED = 'TRANSFER_RECEIVED', 'Transferencia recibida'
        TRANSFER_SENT = 'TRANSFER_SENT', 'Transferencia enviada'
        DEPOSIT_CONFIRMED = 'DEPOSIT_CONFIRMED', 'Deposito confirmado'
        WITHDRAWAL_PROCESSED = 'WITHDRAWAL_PROCESSED', 'Retiro procesado'
        OTP_CODE = 'OTP_CODE', 'Codigo OTP'
        LOAN_APPROVED = 'LOAN_APPROVED', 'Prestamo aprobado'
        LOAN_PAYMENT_DUE = 'LOAN_PAYMENT_DUE', 'Pago de prestamo pendiente'
        MERCHANT_PAYMENT = 'MERCHANT_PAYMENT', 'Pago a comerciante'
        LLO_REWARD = 'LLO_REWARD', 'Recompensa LLO'
        SYSTEM_ALERT = 'SYSTEM_ALERT', 'Alerta del sistema'
        PROMOTION = 'PROMOTION', 'Promocion'

    class Channel(models.TextChoices):
        PUSH = 'PUSH', 'Push'
        SMS = 'SMS', 'SMS'
        WEBSOCKET = 'WEBSOCKET', 'WebSocket'
        EMAIL = 'EMAIL', 'Email'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='usuario',
    )
    notification_type = models.CharField(
        max_length=25,
        choices=NotificationType.choices,
        verbose_name='tipo de notificacion',
    )
    title = models.CharField(max_length=255, verbose_name='titulo')
    message = models.TextField(verbose_name='mensaje')
    data = models.JSONField(default=dict, blank=True, verbose_name='datos adicionales')
    channel = models.CharField(
        max_length=10,
        choices=Channel.choices,
        default=Channel.PUSH,
        verbose_name='canal',
    )
    is_read = models.BooleanField(default=False, verbose_name='leida')
    is_sent = models.BooleanField(default=False, verbose_name='enviada')
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name='fecha de envio')
    read_at = models.DateTimeField(blank=True, null=True, verbose_name='fecha de lectura')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')

    class Meta:
        verbose_name = 'notificacion'
        verbose_name_plural = 'notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read'], name='idx_notification_user_read'),
        ]

    def __str__(self):
        return f'{self.title} -> {self.user} ({self.get_channel_display()})'


class DeviceToken(models.Model):
    """Token de dispositivo para notificaciones push."""

    class Platform(models.TextChoices):
        IOS = 'IOS', 'iOS'
        ANDROID = 'ANDROID', 'Android'
        WEB = 'WEB', 'Web'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tokens',
        verbose_name='usuario',
    )
    token = models.CharField(max_length=500, verbose_name='token del dispositivo')
    platform = models.CharField(
        max_length=10,
        choices=Platform.choices,
        verbose_name='plataforma',
    )
    is_active = models.BooleanField(default=True, verbose_name='activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='fecha de actualizacion')

    class Meta:
        verbose_name = 'token de dispositivo'
        verbose_name_plural = 'tokens de dispositivo'
        unique_together = ['user', 'token']

    def __str__(self):
        return f'{self.user} - {self.get_platform_display()} ({self.token[:20]}...)'


class SMSMessage(models.Model):
    """Registro de mensajes SMS enviados."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        SENT = 'SENT', 'Enviado'
        FAILED = 'FAILED', 'Fallido'
        DELIVERED = 'DELIVERED', 'Entregado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, verbose_name='numero de telefono')
    message = models.TextField(verbose_name='mensaje')
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='estado',
    )
    provider_message_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID del proveedor',
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name='costo',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name='fecha de envio')

    class Meta:
        verbose_name = 'mensaje SMS'
        verbose_name_plural = 'mensajes SMS'
        ordering = ['-created_at']

    def __str__(self):
        return f'SMS a {self.phone_number} - {self.get_status_display()}'
