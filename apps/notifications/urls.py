from django.urls import path

from apps.notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('mark-read/', views.NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('mark-all-read/', views.NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('device-token/', views.DeviceTokenView.as_view(), name='device-token'),
    path('unread-count/', views.UnreadCountView.as_view(), name='unread-count'),
]
