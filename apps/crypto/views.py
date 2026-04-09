import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.crypto.models import (
    CryptoDeposit,
    CryptoWithdrawal,
    ExchangeRate,
    LlanocoinTransaction,
)
from apps.crypto.serializers import (
    CryptoDepositDetailSerializer,
    CryptoDepositSerializer,
    CryptoWithdrawalSerializer,
    ExchangeRateSerializer,
    LlanocoinBuySerializer,
    LlanocoinSellSerializer,
    LlanocoinTransactionSerializer,
)
from apps.crypto.tasks import verify_crypto_deposit

logger = logging.getLogger(__name__)


class CryptoDepositView(APIView):
    """
    POST: Registrar un deposito crypto con tx_hash.
    Lanza la verificacion asincrona on-chain.
    """

    def post(self, request):
        serializer = CryptoDepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Obtener tasa de cambio actual
        rate = ExchangeRate.get_rate(serializer.validated_data['currency'])
        cop_amount = serializer.validated_data['amount'] * rate

        deposit = CryptoDeposit.objects.create(
            user=request.user,
            exchange_rate=rate,
            cop_amount=cop_amount,
            **serializer.validated_data,
        )

        # Lanzar verificacion asincrona
        verify_crypto_deposit.delay(deposit.id)

        detail_serializer = CryptoDepositDetailSerializer(deposit)
        return Response(
            detail_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class CryptoDepositListView(generics.ListAPIView):
    """GET: Listar depositos crypto del usuario autenticado."""

    serializer_class = CryptoDepositDetailSerializer

    def get_queryset(self):
        return CryptoDeposit.objects.filter(user=self.request.user)


class CryptoWithdrawalView(APIView):
    """POST: Solicitar un retiro de criptomonedas."""

    def post(self, request):
        serializer = CryptoWithdrawalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        currency = serializer.validated_data['currency']
        amount = serializer.validated_data['amount']

        # Calcular conversion COP y comision
        rate = ExchangeRate.get_rate(currency)
        cop_amount = amount * rate
        fee_amount = amount * Decimal('0.005')  # 0.5% comision

        with transaction.atomic():
            # Verificar saldo COP suficiente
            wallet = request.user.wallet
            if wallet.balance < cop_amount:
                return Response(
                    {'detail': 'Saldo COP insuficiente para este retiro.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Descontar del saldo
            wallet.balance -= cop_amount
            wallet.save(update_fields=['balance'])

            withdrawal = CryptoWithdrawal.objects.create(
                user=request.user,
                exchange_rate=rate,
                cop_amount=cop_amount,
                fee_amount=fee_amount,
                **serializer.validated_data,
            )

        result_serializer = CryptoWithdrawalSerializer(withdrawal)
        return Response(
            result_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ExchangeRateListView(generics.ListAPIView):
    """GET: Tasas de cambio actuales (publico)."""

    serializer_class = ExchangeRateSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ExchangeRate.objects.all()
    pagination_class = None


class LlanocoinBuyView(APIView):
    """POST: Comprar Llanocoin con saldo COP de la billetera."""

    def post(self, request):
        serializer = LlanocoinBuySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount_cop = serializer.validated_data['amount_cop']
        rate = ExchangeRate.get_rate('LLO')
        amount_llo = amount_cop / rate

        with transaction.atomic():
            wallet = request.user.wallet
            if wallet.balance < amount_cop:
                return Response(
                    {'detail': 'Saldo COP insuficiente.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Descontar COP
            wallet.balance -= amount_cop
            wallet.save(update_fields=['balance'])

            # Crear transaccion LLO
            llo_tx = LlanocoinTransaction.objects.create(
                user=request.user,
                transaction_type=LlanocoinTransaction.TransactionType.BUY,
                amount_llo=amount_llo,
                amount_cop=amount_cop,
                rate=rate,
                status=LlanocoinTransaction.Status.COMPLETED,
            )

        tx_serializer = LlanocoinTransactionSerializer(llo_tx)
        return Response(tx_serializer.data, status=status.HTTP_201_CREATED)


class LlanocoinSellView(APIView):
    """POST: Vender Llanocoin y recibir COP en la billetera."""

    def post(self, request):
        serializer = LlanocoinSellSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount_llo = serializer.validated_data['amount_llo']
        rate = ExchangeRate.get_rate('LLO')
        amount_cop = amount_llo * rate

        with transaction.atomic():
            # Verificar que el usuario tiene suficiente LLO
            # Calculamos el balance LLO del usuario a partir de transacciones
            from django.db.models import Sum, Q

            llo_in = LlanocoinTransaction.objects.filter(
                user=request.user,
                status=LlanocoinTransaction.Status.COMPLETED,
                transaction_type__in=[
                    LlanocoinTransaction.TransactionType.BUY,
                    LlanocoinTransaction.TransactionType.TRANSFER_IN,
                    LlanocoinTransaction.TransactionType.REWARD,
                ],
            ).aggregate(total=Sum('amount_llo'))['total'] or Decimal('0')

            llo_out = LlanocoinTransaction.objects.filter(
                user=request.user,
                status=LlanocoinTransaction.Status.COMPLETED,
                transaction_type__in=[
                    LlanocoinTransaction.TransactionType.SELL,
                    LlanocoinTransaction.TransactionType.TRANSFER_OUT,
                    LlanocoinTransaction.TransactionType.STAKE,
                ],
            ).aggregate(total=Sum('amount_llo'))['total'] or Decimal('0')

            llo_balance = llo_in - llo_out

            if llo_balance < amount_llo:
                return Response(
                    {'detail': f'Saldo LLO insuficiente. Disponible: {llo_balance} LLO'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Acreditar COP
            wallet = request.user.wallet
            wallet.balance += amount_cop
            wallet.save(update_fields=['balance'])

            # Crear transaccion LLO
            llo_tx = LlanocoinTransaction.objects.create(
                user=request.user,
                transaction_type=LlanocoinTransaction.TransactionType.SELL,
                amount_llo=amount_llo,
                amount_cop=amount_cop,
                rate=rate,
                status=LlanocoinTransaction.Status.COMPLETED,
            )

        tx_serializer = LlanocoinTransactionSerializer(llo_tx)
        return Response(tx_serializer.data, status=status.HTTP_201_CREATED)


class LlanocoinTransactionListView(generics.ListAPIView):
    """GET: Listar transacciones Llanocoin del usuario autenticado."""

    serializer_class = LlanocoinTransactionSerializer

    def get_queryset(self):
        return LlanocoinTransaction.objects.filter(user=self.request.user)
