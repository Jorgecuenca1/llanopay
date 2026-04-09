from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.transfers import views

router = DefaultRouter()
router.register(r'scheduled', views.ScheduledTransferViewSet, basename='scheduled-transfer')

app_name = 'transfers'

urlpatterns = [
    path('send/', views.TransferCreateView.as_view(), name='transfer-create'),
    path('confirm/', views.TransferConfirmView.as_view(), name='transfer-confirm'),
    path('list/', views.TransferListView.as_view(), name='transfer-list'),
    path('<uuid:pk>/', views.TransferDetailView.as_view(), name='transfer-detail'),
    path('limits/', views.TransferLimitView.as_view(), name='transfer-limits'),
    path('', include(router.urls)),
]
