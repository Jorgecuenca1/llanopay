from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('usuarios/', views.users_view, name='users'),
    path('billeteras/', views.wallet_overview_view, name='wallets'),
    path('transacciones/', views.transactions_view, name='transactions'),
    path('transferencias/', views.transfers_view, name='transfers'),
    path('crypto/', views.crypto_view, name='crypto'),
    path('marketplace/', views.merchants_view, name='merchants'),
    path('microcreditos/', views.microcredits_view, name='microcredits'),
    path('notificaciones/', views.notifications_view, name='notifications'),
    path('llanocoin/', views.llanocoin_view, name='llanocoin'),
    path('reportes/', views.reports_view, name='reports'),
]
