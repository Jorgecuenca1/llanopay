from django.urls import path

from apps.wallet import views

app_name = 'wallet'

urlpatterns = [
    path('', views.WalletDetailView.as_view(), name='wallet-detail'),
    path('balance/', views.BalanceSummaryView.as_view(), name='balance-summary'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
]
