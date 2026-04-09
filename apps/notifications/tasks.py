import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_push_notification(self, notification_id):
    """Enviar una notificacion push a traves de FCM/APNs."""
    from apps.notifications.models import Notification, DeviceToken

    try:
        notification = Notification.objects.select_related('user').get(pk=notification_id)
    except Notification.DoesNotExist:
        logger.error('Notificacion %s no encontrada.', notification_id)
        return

    device_tokens = DeviceToken.objects.filter(
        user=notification.user,
        is_active=True,
    )

    if not device_tokens.exists():
        logger.warning(
            'No hay tokens de dispositivo activos para el usuario %s.',
            notification.user_id,
        )
        return

    for device_token in device_tokens:
        try:
            # TODO: integrar con Firebase Cloud Messaging o APNs
            logger.info(
                'Enviando push a %s (%s): %s',
                device_token.token[:20],
                device_token.get_platform_display(),
                notification.title,
            )
        except Exception as exc:
            logger.error(
                'Error enviando push a token %s: %s',
                device_token.token[:20],
                exc,
            )
            raise self.retry(exc=exc)

    notification.is_sent = True
    notification.sent_at = timezone.now()
    notification.save(update_fields=['is_sent', 'sent_at'])


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_notification(self, notification_id):
    """Enviar una notificacion por SMS."""
    from apps.notifications.models import Notification, SMSMessage

    try:
        notification = Notification.objects.select_related('user').get(pk=notification_id)
    except Notification.DoesNotExist:
        logger.error('Notificacion %s no encontrada.', notification_id)
        return

    phone_number = str(notification.user.phone_number)

    sms = SMSMessage.objects.create(
        phone_number=phone_number,
        message=f'{notification.title}: {notification.message}',
    )

    try:
        # TODO: integrar con proveedor de SMS (Twilio, AWS SNS, etc.)
        logger.info('Enviando SMS a %s: %s', phone_number, notification.title)
        sms.status = SMSMessage.Status.SENT
        sms.sent_at = timezone.now()
        sms.save(update_fields=['status', 'sent_at'])

        notification.is_sent = True
        notification.sent_at = timezone.now()
        notification.save(update_fields=['is_sent', 'sent_at'])

    except Exception as exc:
        sms.status = SMSMessage.Status.FAILED
        sms.save(update_fields=['status'])
        logger.error('Error enviando SMS a %s: %s', phone_number, exc)
        raise self.retry(exc=exc)


@shared_task
def send_bulk_notification(user_ids, title, message, notification_type):
    """Enviar notificacion masiva a multiples usuarios."""
    from apps.notifications.models import Notification

    notifications = []
    for user_id in user_ids:
        notifications.append(
            Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                channel=Notification.Channel.PUSH,
            )
        )

    created = Notification.objects.bulk_create(notifications)
    logger.info('Creadas %d notificaciones masivas.', len(created))

    for notification in created:
        send_push_notification.delay(str(notification.pk))

    return len(created)


@shared_task
def cleanup_old_notifications():
    """Eliminar notificaciones con mas de 90 dias de antiguedad."""
    from apps.notifications.models import Notification

    cutoff = timezone.now() - timedelta(days=90)
    count, _ = Notification.objects.filter(created_at__lt=cutoff).delete()
    logger.info('Eliminadas %d notificaciones antiguas (> 90 dias).', count)
    return count
