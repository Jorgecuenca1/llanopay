from decimal import Decimal

from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.wallet.models import Wallet, Transaction
from apps.wallet.serializers import (
    WalletSerializer,
    TransactionSerializer,
    TransactionFilterSerializer,
    BalanceSummarySerializer,
)


class WalletDetailView(generics.RetrieveAPIView):
    """GET - Obtener la billetera del usuario autenticado con sus saldos."""

    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        wallet, _created = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


class TransactionListView(generics.ListAPIView):
    """GET - Listar transacciones del usuario con filtros opcionales."""

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        wallet, _created = Wallet.objects.get_or_create(user=self.request.user)
        queryset = Transaction.objects.filter(wallet=wallet)

        filter_serializer = TransactionFilterSerializer(data=self.request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        if 'date_from' in filters:
            queryset = queryset.filter(created_at__gte=filters['date_from'])
        if 'date_to' in filters:
            queryset = queryset.filter(created_at__lte=filters['date_to'])
        if 'transaction_type' in filters:
            queryset = queryset.filter(transaction_type=filters['transaction_type'])
        if 'currency' in filters:
            queryset = queryset.filter(currency=filters['currency'])

        return queryset


class TransactionDetailView(generics.RetrieveAPIView):
    """GET - Obtener detalle de una transaccion especifica del usuario."""

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        wallet, _created = Wallet.objects.get_or_create(user=self.request.user)
        return Transaction.objects.filter(wallet=wallet)


class BalanceSummaryView(APIView):
    """GET - Resumen de saldos incluyendo equivalente en COP de LLO."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, _created = Wallet.objects.get_or_create(user=request.user)
        llo_cop_rate = Decimal(str(getattr(settings, 'LLO_COP_RATE', 1000)))
        llo_cop_equivalent = wallet.balance_llo * llo_cop_rate

        serializer = BalanceSummarySerializer({
            'balance_cop': wallet.balance_cop,
            'balance_llo': wallet.balance_llo,
            'llo_cop_equivalent': llo_cop_equivalent,
        })
        return Response(serializer.data, status=status.HTTP_200_OK)
