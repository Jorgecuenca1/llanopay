from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.notifications.models import Notification

User = get_user_model()


class NotificationModelTests(TestCase):
    """Tests para la creacion de notificaciones."""

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='+573001234567',
            password='testpass123',
            document_type='CC',
            document_number='123456789',
            first_name='Test',
            last_name='User',
        )

    def test_create_notification(self):
        notification = Notification.objects.create(
            user=self.user,
            notification_type=Notification.NotificationType.TRANSFER_RECEIVED,
            title='Transferencia recibida',
            message='Has recibido COP 50,000.00 de Juan.',
            channel=Notification.Channel.PUSH,
        )
        self.assertEqual(notification.user, self.user)
        self.assertFalse(notification.is_read)
        self.assertFalse(notification.is_sent)
        self.assertIsNone(notification.sent_at)
        self.assertIsNone(notification.read_at)

    def test_notification_default_data(self):
        notification = Notification.objects.create(
            user=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title='Alerta',
            message='Mantenimiento programado.',
        )
        self.assertEqual(notification.data, {})
        self.assertEqual(notification.channel, Notification.Channel.PUSH)

    def test_notification_ordering(self):
        n1 = Notification.objects.create(
            user=self.user,
            notification_type=Notification.NotificationType.PROMOTION,
            title='Promo 1',
            message='Primera promocion.',
        )
        n2 = Notification.objects.create(
            user=self.user,
            notification_type=Notification.NotificationType.PROMOTION,
            title='Promo 2',
            message='Segunda promocion.',
        )
        notifications = list(Notification.objects.filter(user=self.user))
        self.assertEqual(notifications[0].pk, n2.pk)
        self.assertEqual(notifications[1].pk, n1.pk)


class NotificationAPITests(TestCase):
    """Tests para los endpoints de notificaciones."""

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='+573009876543',
            password='testpass123',
            document_type='CC',
            document_number='987654321',
            first_name='API',
            last_name='Tester',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.n1 = Notification.objects.create(
            user=self.user,
            notification_type=Notification.NotificationType.TRANSFER_RECEIVED,
            title='Transferencia 1',
            message='Has recibido dinero.',
        )
        self.n2 = Notification.objects.create(
            user=self.user,
            notification_type=Notification.NotificationType.DEPOSIT_CONFIRMED,
            title='Deposito confirmado',
            message='Tu deposito fue exitoso.',
            is_read=True,
        )

    def test_list_notifications(self):
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_unread_notifications(self):
        response = self.client.get('/api/notifications/?is_read=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Transferencia 1')

    def test_mark_read(self):
        response = self.client.post(
            '/api/notifications/mark-read/',
            {'notification_ids': [str(self.n1.pk)]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['marked_read'], 1)

        self.n1.refresh_from_db()
        self.assertTrue(self.n1.is_read)
        self.assertIsNotNone(self.n1.read_at)

    def test_mark_all_read(self):
        response = self.client.post('/api/notifications/mark-all-read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['marked_read'], 1)  # solo n1 estaba sin leer

        unread = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread, 0)

    def test_unread_count(self):
        response = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

    def test_register_device_token(self):
        response = self.client.post(
            '/api/notifications/device-token/',
            {'token': 'fcm_test_token_abc123', 'platform': 'ANDROID'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['platform'], 'ANDROID')

    def test_unauthenticated_access_denied(self):
        client = APIClient()
        response = client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
