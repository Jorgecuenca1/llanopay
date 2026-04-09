import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer para notificaciones en tiempo real."""

    async def connect(self):
        user = self.scope.get('user')
        if user is None or user.is_anonymous:
            await self.close()
            return

        self.group_name = f'notifications_{user.pk}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info('WebSocket conectado para usuario %s.', user.pk)

    async def disconnect(self, close_code):
        user = self.scope.get('user')
        if user and not user.is_anonymous:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info('WebSocket desconectado para usuario %s.', user.pk)

    async def receive_json(self, content, **kwargs):
        """Procesar mensajes del cliente (ej. marcar como leida)."""
        msg_type = content.get('type')

        if msg_type == 'mark_read':
            notification_id = content.get('notification_id')
            if notification_id:
                await self.mark_notification_read(notification_id)

    async def mark_notification_read(self, notification_id):
        """Marcar una notificacion como leida desde el WebSocket."""
        from channels.db import database_sync_to_async
        from django.utils import timezone as tz

        from apps.notifications.models import Notification

        @database_sync_to_async
        def _mark_read():
            return Notification.objects.filter(
                pk=notification_id,
                user=self.scope['user'],
                is_read=False,
            ).update(is_read=True, read_at=tz.now())

        updated = await _mark_read()
        if updated:
            await self.send_json({
                'type': 'notification_read',
                'notification_id': str(notification_id),
            })

    async def send_notification(self, event):
        """Enviar nueva notificacion al cliente conectado."""
        await self.send_json({
            'type': 'new_notification',
            'notification': event['notification'],
        })
