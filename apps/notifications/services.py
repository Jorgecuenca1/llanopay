import logging

from django.utils import timezone

from apps.notifications.models import Notification, SMSMessage

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio centralizado para crear y enviar notificaciones."""

    @staticmethod
    def create_and_send(user, title, message, notification_type, channel='PUSH', data=None):
        """Crear una notificacion y despacharla por el canal indicado."""
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            channel=channel,
            data=data or {},
        )

        # Despachar segun el canal
        if channel == Notification.Channel.PUSH:
            from apps.notifications.tasks import send_push_notification
            send_push_notification.delay(str(notification.pk))

        elif channel == Notification.Channel.SMS:
            from apps.notifications.tasks import send_sms_notification
            send_sms_notification.delay(str(notification.pk))

        elif channel == Notification.Channel.WEBSOCKET:
            NotificationService._send_websocket(notification)

        return notification

    @staticmethod
    def _send_websocket(notification):
        """Enviar notificacion por WebSocket al grupo del usuario."""
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            channel_layer = get_channel_layer()
            group_name = f'notifications_{notification.user_id}'

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'notification': {
                        'id': str(notification.pk),
                        'notification_type': notification.notification_type,
                        'title': notification.title,
                        'message': notification.message,
                        'data': notification.data,
                        'created_at': notification.created_at.isoformat(),
                    },
                },
            )

            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.save(update_fields=['is_sent', 'sent_at'])

        except Exception:
            logger.exception(
                'Error enviando notificacion WebSocket al usuario %s.',
                notification.user_id,
            )

    @staticmethod
    def send_transfer_notification(transfer):
        """Enviar notificaciones de transferencia a emisor y receptor."""
        # Notificacion al emisor
        NotificationService.create_and_send(
            user=transfer.sender,
            title='Transferencia enviada',
            message=(
                f'Has enviado {transfer.currency} {transfer.amount:,.2f} '
                f'a {transfer.receiver.full_name}.'
            ),
            notification_type=Notification.NotificationType.TRANSFER_SENT,
            channel=Notification.Channel.PUSH,
            data={
                'transfer_id': str(transfer.pk),
                'amount': str(transfer.amount),
                'currency': transfer.currency,
            },
        )

        # Notificacion al receptor
        NotificationService.create_and_send(
            user=transfer.receiver,
            title='Transferencia recibida',
            message=(
                f'Has recibido {transfer.currency} {transfer.amount:,.2f} '
                f'de {transfer.sender.full_name}.'
            ),
            notification_type=Notification.NotificationType.TRANSFER_RECEIVED,
            channel=Notification.Channel.PUSH,
            data={
                'transfer_id': str(transfer.pk),
                'amount': str(transfer.amount),
                'currency': transfer.currency,
            },
        )

    @staticmethod
    def send_deposit_notification(deposit):
        """Enviar notificacion de deposito confirmado."""
        NotificationService.create_and_send(
            user=deposit.user,
            title='Deposito confirmado',
            message=(
                f'Tu deposito de {deposit.currency} {deposit.amount:,.2f} '
                f'ha sido confirmado exitosamente.'
            ),
            notification_type=Notification.NotificationType.DEPOSIT_CONFIRMED,
            channel=Notification.Channel.PUSH,
            data={
                'deposit_id': str(deposit.pk),
                'amount': str(deposit.amount),
                'currency': deposit.currency,
            },
        )

    @staticmethod
    def send_otp_sms(phone_number, otp_code):
        """Enviar codigo OTP por SMS directamente (sin notificacion de usuario)."""
        sms = SMSMessage.objects.create(
            phone_number=str(phone_number),
            message=f'LlanoPay - Tu codigo de verificacion es: {otp_code}. No lo compartas con nadie.',
        )

        try:
            # TODO: integrar con proveedor de SMS (Twilio, AWS SNS, etc.)
            logger.info('Enviando OTP SMS a %s.', phone_number)
            sms.status = SMSMessage.Status.SENT
            sms.sent_at = timezone.now()
            sms.save(update_fields=['status', 'sent_at'])
        except Exception:
            sms.status = SMSMessage.Status.FAILED
            sms.save(update_fields=['status'])
            logger.exception('Error enviando OTP SMS a %s.', phone_number)
            raise

        return sms
