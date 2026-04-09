from django.urls import path

from apps.crypto import views

app_name = 'crypto'

urlpatterns = [
    # Depositos crypto
    path(
        'deposits/',
        views.CryptoDepositView.as_view(),
        name='deposit-create',
    ),
    path(
        'deposits/list/',
        views.CryptoDepositListView.as_view(),
        name='deposit-list',
    ),

    # Retiros crypto
    path(
        'withdrawals/',
        views.CryptoWithdrawalView.as_view(),
        name='withdrawal-create',
    ),

    # Tasas de cambio
    path(
        'rates/',
        views.ExchangeRateListView.as_view(),
        name='exchange-rates',
    ),

    # Llanocoin
    path(
        'llanocoin/buy/',
        views.LlanocoinBuyView.as_view(),
        name='llanocoin-buy',
    ),
    path(
        'llanocoin/sell/',
        views.LlanocoinSellView.as_view(),
        name='llanocoin-sell',
    ),
    path(
        'llanocoin/transactions/',
        views.LlanocoinTransactionListView.as_view(),
        name='llanocoin-transactions',
    ),
]
