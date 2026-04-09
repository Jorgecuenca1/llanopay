from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification, DeviceToken
from apps.notifications.serializers import (
    NotificationSerializer,
    NotificationMarkReadSerializer,
    DeviceTokenSerializer,
)


class NotificationListView(generics.ListAPIView):
    """GET - Listar notificaciones del usuario autenticado con filtro de lectura."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() in ('true', '1'))
        return queryset


class NotificationMarkReadView(APIView):
    """POST - Marcar una o varias notificaciones como leidas."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        now = timezone.now()
        updated = Notification.objects.filter(
            user=request.user,
            pk__in=serializer.validated_data['notification_ids'],
            is_read=False,
        ).update(is_read=True, read_at=now)

        return Response(
            {'marked_read': updated},
            status=status.HTTP_200_OK,
        )


class NotificationMarkAllReadView(APIView):
    """POST - Marcar todas las notificaciones del usuario como leidas."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        now = timezone.now()
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(is_read=True, read_at=now)

        return Response(
            {'marked_read': updated},
            status=status.HTTP_200_OK,
        )


class DeviceTokenView(APIView):
    """POST - Registrar o actualizar token de dispositivo para push."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeviceTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnreadCountView(APIView):
    """GET - Obtener el conteo de notificaciones no leidas."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)
