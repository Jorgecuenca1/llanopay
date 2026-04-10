from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'cards', views.VirtualCardViewSet, basename='virtual-cards')

app_name = 'global_features'

urlpatterns = [
    # Countries & Currencies (public)
    path('countries/', views.CountryListView.as_view(), name='countries'),
    path('currencies/', views.CurrencyListView.as_view(), name='currencies'),
    path('convert/', views.CurrencyConvertView.as_view(), name='convert'),

    # Multi-balance
    path('balances/', views.MultiBalanceListView.as_view(), name='balances'),

    # QR Payments
    path('qr/', views.QRPaymentCreateView.as_view(), name='qr-create'),
    path('qr/list/', views.QRPaymentListView.as_view(), name='qr-list'),
    path('qr/<str:code>/', views.QRPaymentDetailView.as_view(), name='qr-detail'),
    path('qr/<str:code>/pay/', views.QRPaymentPayView.as_view(), name='qr-pay'),

    # Mobile top-ups (recargas)
    path('mobile-topup/', views.MobileTopupCreateView.as_view(), name='mobile-topup'),

    # Bill payments
    path('bills/', views.BillPaymentCreateView.as_view(), name='bills'),

    # Referrals
    path('referral/code/', views.MyReferralCodeView.as_view(), name='referral-code'),
    path('referral/list/', views.MyReferralsView.as_view(), name='referral-list'),
    path('referral/apply/', views.ApplyReferralCodeView.as_view(), name='referral-apply'),

    # Rewards
    path('rewards/', views.MyRewardsView.as_view(), name='rewards'),
    path('rewards/history/', views.RewardHistoryView.as_view(), name='rewards-history'),
    path('rewards/redeem/', views.RedeemPointsView.as_view(), name='rewards-redeem'),

    # Wallet top-up
    path('wallet/topup/', views.WalletTopupCreateView.as_view(), name='wallet-topup'),

    # Cards
    path('', include(router.urls)),
]
