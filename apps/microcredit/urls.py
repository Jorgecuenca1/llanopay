from django.urls import path

from apps.microcredit import views

app_name = 'microcredit'

urlpatterns = [
    path(
        'profile/',
        views.CreditProfileView.as_view(),
        name='credit-profile',
    ),
    path(
        'products/',
        views.MicrocreditProductListView.as_view(),
        name='product-list',
    ),
    path(
        'request/',
        views.MicrocreditRequestView.as_view(),
        name='microcredit-request',
    ),
    path(
        'loans/',
        views.MicrocreditListView.as_view(),
        name='microcredit-list',
    ),
    path(
        'loans/<uuid:pk>/',
        views.MicrocreditDetailView.as_view(),
        name='microcredit-detail',
    ),
    path(
        'pay/',
        views.MicrocreditPaymentView.as_view(),
        name='microcredit-payment',
    ),
    path(
        'score/recalculate/',
        views.CreditScoreRecalculateView.as_view(),
        name='credit-score-recalculate',
    ),
]
