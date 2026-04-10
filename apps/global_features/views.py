"""Views for global features."""
from datetime import timedelta
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.global_features.models import (
    Country, Currency, MultiBalance, QRPayment, MobileTopup, BillPayment,
    ReferralCode, Referral, VirtualCard, VirtualCardTransaction,
    RewardPoints, RewardTransaction, WalletTopup,
)
from apps.global_features.serializers import (
    CountrySerializer, CurrencySerializer, MultiBalanceSerializer,
    QRPaymentSerializer, MobileTopupSerializer, BillPaymentSerializer,
    ReferralCodeSerializer, ReferralSerializer, VirtualCardSerializer,
    VirtualCardTransactionSerializer,
    RewardPointsSerializer, RewardTransactionSerializer, WalletTopupSerializer,
)
from apps.wallet.models import Wallet, Transaction as WalletTx


# ==============================================================
# COUNTRIES & CURRENCIES (PUBLIC)
# ==============================================================

class CountryListView(generics.ListAPIView):
    """Public list of all supported countries."""
    queryset = Country.objects.filter(is_supported=True)
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class CurrencyListView(generics.ListAPIView):
    """Public list of all active currencies with rates."""
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class CurrencyConvertView(APIView):
    """Convert amount from one currency to another."""
    permission_classes = [AllowAny]

    def get(self, request):
        from_code = request.query_params.get('from', 'USD').upper()
        to_code = request.query_params.get('to', 'USD').upper()
        amount = request.query_params.get('amount', '1')

        try:
            amount = Decimal(amount)
            from_curr = Currency.objects.get(code=from_code)
            to_curr = Currency.objects.get(code=to_code)
        except (Currency.DoesNotExist, ValueError):
            return Response({'detail': 'Currency not found'}, status=404)

        usd_amount = from_curr.to_usd(amount)
        result = to_curr.from_usd(usd_amount)

        return Response({
            'from': from_code,
            'to': to_code,
            'amount': str(amount),
            'result': str(result),
            'usd_equivalent': str(usd_amount),
            'rate': str(to_curr.rate_to_usd / from_curr.rate_to_usd) if from_curr.rate_to_usd else '0',
        })


# ==============================================================
# MULTI BALANCE
# ==============================================================

class MultiBalanceListView(generics.ListAPIView):
    """User's multi-currency balances."""
    serializer_class = MultiBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MultiBalance.objects.filter(user=self.request.user).select_related('currency')


# ==============================================================
# QR PAYMENTS
# ==============================================================

class QRPaymentCreateView(generics.CreateAPIView):
    """Generate a QR payment request."""
    serializer_class = QRPaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Default expiry: 24 hours
        expires = timezone.now() + timedelta(hours=24)
        serializer.save(receiver=self.request.user, expires_at=expires)


class QRPaymentListView(generics.ListAPIView):
    """User's QR payments."""
    serializer_class = QRPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        from django.db.models import Q
        return QRPayment.objects.filter(Q(receiver=user) | Q(payer=user)).order_by('-created_at')


class QRPaymentDetailView(generics.RetrieveAPIView):
    """Get QR payment by code (for scanning)."""
    serializer_class = QRPaymentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'code'
    queryset = QRPayment.objects.all()


class QRPaymentPayView(APIView):
    """Pay a QR payment."""
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        try:
            qr = QRPayment.objects.select_for_update().get(code=code)
        except QRPayment.DoesNotExist:
            return Response({'detail': 'QR no encontrado'}, status=404)

        if qr.status != QRPayment.Status.PENDING:
            return Response({'detail': 'Este QR ya no es valido'}, status=400)

        if qr.expires_at and qr.expires_at < timezone.now():
            qr.status = QRPayment.Status.EXPIRED
            qr.save()
            return Response({'detail': 'Este QR ha expirado'}, status=400)

        if qr.receiver_id == request.user.id:
            return Response({'detail': 'No puedes pagar tu propio QR'}, status=400)

        # Get amount from request if QR has no fixed amount
        amount = qr.amount or Decimal(str(request.data.get('amount', 0)))
        if amount <= 0:
            return Response({'detail': 'Monto invalido'}, status=400)

        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            payer_wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
            receiver_wallet, _ = Wallet.objects.select_for_update().get_or_create(user=qr.receiver)

            currency = qr.currency
            if currency == 'COP':
                if payer_wallet.balance_cop < amount:
                    return Response({'detail': 'Saldo COP insuficiente'}, status=400)
                payer_wallet.balance_cop -= amount
                receiver_wallet.balance_cop += amount
            elif currency == 'LLO':
                if payer_wallet.balance_llo < amount:
                    return Response({'detail': 'Saldo LLO insuficiente'}, status=400)
                payer_wallet.balance_llo -= amount
                receiver_wallet.balance_llo += amount
            else:
                return Response({'detail': f'Moneda {currency} no soportada para pagos QR'}, status=400)

            payer_wallet.save()
            receiver_wallet.save()

            # Create transactions
            WalletTx.objects.create(
                wallet=payer_wallet,
                transaction_type=WalletTx.TransactionType.TRANSFER_OUT,
                amount=amount,
                currency=currency,
                balance_after=payer_wallet.balance_cop if currency == 'COP' else payer_wallet.balance_llo,
                reference=qr.code,
                description=f'Pago QR a {qr.receiver.first_name} {qr.receiver.last_name}'.strip() or qr.description,
                status=WalletTx.Status.COMPLETED,
                metadata={'qr_code': qr.code},
            )
            WalletTx.objects.create(
                wallet=receiver_wallet,
                transaction_type=WalletTx.TransactionType.TRANSFER_IN,
                amount=amount,
                currency=currency,
                balance_after=receiver_wallet.balance_cop if currency == 'COP' else receiver_wallet.balance_llo,
                reference=qr.code,
                description=f'Pago QR de {request.user.first_name} {request.user.last_name}'.strip(),
                status=WalletTx.Status.COMPLETED,
                metadata={'qr_code': qr.code},
            )

            qr.status = QRPayment.Status.PAID
            qr.payer = request.user
            qr.amount = amount
            qr.paid_at = timezone.now()
            qr.save()

            # Reward points
            try:
                rp, _ = RewardPoints.objects.get_or_create(user=request.user)
                rp.add_points(int(float(amount) / 1000) if currency == 'COP' else 1, f'Pago QR')
            except Exception:
                pass

        return Response({
            'message': 'Pago exitoso',
            'qr': QRPaymentSerializer(qr).data,
        })


# ==============================================================
# MOBILE TOP-UPS
# ==============================================================

class MobileTopupCreateView(generics.ListCreateAPIView):
    """Create or list mobile top-ups."""
    serializer_class = MobileTopupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MobileTopup.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        currency = serializer.validated_data.get('currency', 'COP')

        # Deduct from user wallet
        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
            if currency == 'COP':
                if wallet.balance_cop < amount:
                    return Response({'detail': 'Saldo insuficiente'}, status=400)
                wallet.balance_cop -= amount
            else:
                if wallet.balance_llo < amount:
                    return Response({'detail': 'Saldo LLO insuficiente'}, status=400)
                wallet.balance_llo -= amount
            wallet.save()

            topup = serializer.save(
                user=request.user,
                status=MobileTopup.Status.COMPLETED,
                completed_at=timezone.now(),
                reference=f'TOPUP-{timezone.now().strftime("%Y%m%d%H%M%S")}',
            )

            WalletTx.objects.create(
                wallet=wallet,
                transaction_type=WalletTx.TransactionType.WITHDRAWAL,
                amount=amount,
                currency=currency,
                balance_after=wallet.balance_cop if currency == 'COP' else wallet.balance_llo,
                reference=topup.reference,
                description=f'Recarga celular {topup.phone_number} ({topup.operator})',
                status=WalletTx.Status.COMPLETED,
                metadata={'topup_id': str(topup.id)},
            )

            # Reward points
            try:
                rp, _ = RewardPoints.objects.get_or_create(user=request.user)
                rp.add_points(int(float(amount) / 1000) if currency == 'COP' else 1, 'Recarga celular')
            except Exception:
                pass

        return Response(MobileTopupSerializer(topup).data, status=status.HTTP_201_CREATED)


# ==============================================================
# BILL PAYMENTS
# ==============================================================

class BillPaymentCreateView(generics.ListCreateAPIView):
    """Create or list bill payments."""
    serializer_class = BillPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BillPayment.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        currency = serializer.validated_data.get('currency', 'COP')

        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
            if currency == 'COP':
                if wallet.balance_cop < amount:
                    return Response({'detail': 'Saldo insuficiente'}, status=400)
                wallet.balance_cop -= amount
            else:
                if wallet.balance_llo < amount:
                    return Response({'detail': 'Saldo LLO insuficiente'}, status=400)
                wallet.balance_llo -= amount
            wallet.save()

            bill = serializer.save(
                user=request.user,
                status=BillPayment.Status.COMPLETED,
                completed_at=timezone.now(),
                reference=f'BILL-{timezone.now().strftime("%Y%m%d%H%M%S")}',
            )

            WalletTx.objects.create(
                wallet=wallet,
                transaction_type=WalletTx.TransactionType.WITHDRAWAL,
                amount=amount,
                currency=currency,
                balance_after=wallet.balance_cop if currency == 'COP' else wallet.balance_llo,
                reference=bill.reference,
                description=f'Pago {bill.get_category_display()} - {bill.company}',
                status=WalletTx.Status.COMPLETED,
                metadata={'bill_id': str(bill.id)},
            )

            try:
                rp, _ = RewardPoints.objects.get_or_create(user=request.user)
                rp.add_points(int(float(amount) / 1000) if currency == 'COP' else 1, 'Pago de servicio')
            except Exception:
                pass

        return Response(BillPaymentSerializer(bill).data, status=status.HTTP_201_CREATED)


# ==============================================================
# REFERRALS
# ==============================================================

class MyReferralCodeView(APIView):
    """Get or create the user's referral code."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rc, _ = ReferralCode.objects.get_or_create(user=request.user)
        return Response(ReferralCodeSerializer(rc).data)


class MyReferralsView(generics.ListAPIView):
    """List people the user has referred."""
    serializer_class = ReferralSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Referral.objects.filter(referrer=self.request.user)


class ApplyReferralCodeView(APIView):
    """Apply a referral code (during/after registration)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        if not code:
            return Response({'detail': 'Codigo requerido'}, status=400)

        if hasattr(request.user, 'referred_by'):
            return Response({'detail': 'Ya usaste un codigo de referido'}, status=400)

        try:
            referrer_code = ReferralCode.objects.get(code=code)
        except ReferralCode.DoesNotExist:
            return Response({'detail': 'Codigo invalido'}, status=400)

        if referrer_code.user_id == request.user.id:
            return Response({'detail': 'No puedes referirte a ti mismo'}, status=400)

        referral = Referral.objects.create(
            referrer=referrer_code.user,
            referred=request.user,
            bonus_amount=Decimal('5000'),
            bonus_currency='COP',
            bonus_paid=True,
        )

        # Pay bonus to referrer
        wallet, _ = Wallet.objects.get_or_create(user=referrer_code.user)
        wallet.balance_cop += Decimal('5000')
        wallet.save()
        WalletTx.objects.create(
            wallet=wallet,
            transaction_type=WalletTx.TransactionType.DEPOSIT,
            amount=Decimal('5000'),
            currency='COP',
            balance_after=wallet.balance_cop,
            reference=f'REF-{referral.id}',
            description=f'Bono por referir a {request.user.first_name}',
            status=WalletTx.Status.COMPLETED,
            metadata={'referral_id': referral.id},
        )

        # Pay bonus to referred
        my_wallet, _ = Wallet.objects.get_or_create(user=request.user)
        my_wallet.balance_cop += Decimal('5000')
        my_wallet.save()
        WalletTx.objects.create(
            wallet=my_wallet,
            transaction_type=WalletTx.TransactionType.DEPOSIT,
            amount=Decimal('5000'),
            currency='COP',
            balance_after=my_wallet.balance_cop,
            reference=f'REF-{referral.id}',
            description='Bono de bienvenida por referido',
            status=WalletTx.Status.COMPLETED,
            metadata={'referral_id': referral.id},
        )

        # Update referrer stats
        referrer_code.total_referrals += 1
        referrer_code.total_earned += Decimal('5000')
        referrer_code.save()

        return Response({
            'message': 'Codigo aplicado! Has recibido un bono de bienvenida de $5,000 COP',
            'referral': ReferralSerializer(referral).data,
        })


# ==============================================================
# VIRTUAL CARDS
# ==============================================================

class VirtualCardViewSet(viewsets.ModelViewSet):
    """CRUD for virtual cards."""
    serializer_class = VirtualCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VirtualCard.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Default expiry: 3 years from now
        now = timezone.now()
        expiry_year = now.year + 3
        full_name = f'{self.request.user.first_name} {self.request.user.last_name}'.strip().upper()
        serializer.save(
            user=self.request.user,
            card_holder_name=full_name or 'SUPERNOVA USER',
            expiry_month=now.month,
            expiry_year=expiry_year,
        )

    @action(detail=True, methods=['post'])
    def freeze(self, request, pk=None):
        card = self.get_object()
        card.status = VirtualCard.Status.FROZEN
        card.save()
        return Response(VirtualCardSerializer(card).data)

    @action(detail=True, methods=['post'])
    def unfreeze(self, request, pk=None):
        card = self.get_object()
        card.status = VirtualCard.Status.ACTIVE
        card.save()
        return Response(VirtualCardSerializer(card).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        card = self.get_object()
        card.status = VirtualCard.Status.CANCELLED
        card.save()
        return Response(VirtualCardSerializer(card).data)

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get transactions for a card."""
        card = self.get_object()
        txs = card.transactions.all()
        return Response(VirtualCardTransactionSerializer(txs, many=True).data)

    @action(detail=True, methods=['post'])
    def topup(self, request, pk=None):
        """Top up the card from wallet balance."""
        card = self.get_object()
        amount_str = request.data.get('amount', '0')
        try:
            amount = Decimal(str(amount_str))
        except Exception:
            return Response({'detail': 'Monto invalido'}, status=400)
        if amount <= 0:
            return Response({'detail': 'Monto debe ser positivo'}, status=400)

        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
            # Card always uses USD/COP - convert if needed
            cop_needed = amount
            if card.currency == 'USD':
                # 1 USD = 4100 COP approx
                try:
                    usd_curr = Currency.objects.get(code='USD')
                    cop_needed = (amount * usd_curr.rate_to_usd).quantize(Decimal('0.01'))
                except Currency.DoesNotExist:
                    cop_needed = amount * Decimal('4100')

            if wallet.balance_cop < cop_needed:
                return Response({'detail': f'Saldo COP insuficiente. Necesitas {cop_needed}'}, status=400)

            wallet.balance_cop -= cop_needed
            wallet.save(update_fields=['balance_cop', 'updated_at'])

            card.balance += amount
            card.save(update_fields=['balance'])

            # Record card tx
            VirtualCardTransaction.objects.create(
                card=card,
                transaction_type=VirtualCardTransaction.TxType.TOPUP,
                amount=amount,
                currency=card.currency,
                merchant_name='Recarga desde Wallet',
                description=f'Recarga de {cop_needed} COP',
            )

            # Record wallet tx
            WalletTx.objects.create(
                wallet=wallet,
                transaction_type=WalletTx.TransactionType.WITHDRAWAL,
                amount=cop_needed,
                currency='COP',
                balance_after=wallet.balance_cop,
                reference=f'CARD-{card.id}',
                description=f'Recarga tarjeta {card.masked_number}',
                status=WalletTx.Status.COMPLETED,
                metadata={'card_id': str(card.id)},
            )

        return Response({
            'message': 'Tarjeta recargada',
            'card': VirtualCardSerializer(card).data,
        })

    @action(detail=True, methods=['post'])
    def simulate_purchase(self, request, pk=None):
        """Simulate a purchase with the card (for demo)."""
        card = self.get_object()
        amount_str = request.data.get('amount', '0')
        merchant = request.data.get('merchant', 'Comercio')
        try:
            amount = Decimal(str(amount_str))
        except Exception:
            return Response({'detail': 'Monto invalido'}, status=400)

        if card.status != VirtualCard.Status.ACTIVE:
            return Response({'detail': 'La tarjeta no esta activa'}, status=400)

        if card.balance < amount:
            return Response({'detail': 'Saldo insuficiente en la tarjeta'}, status=400)

        if card.monthly_spent + amount > card.spending_limit:
            return Response({'detail': 'Excede el limite mensual'}, status=400)

        card.balance -= amount
        card.monthly_spent += amount
        card.total_spent += amount
        card.save(update_fields=['balance', 'monthly_spent', 'total_spent'])

        tx = VirtualCardTransaction.objects.create(
            card=card,
            transaction_type=VirtualCardTransaction.TxType.PURCHASE,
            amount=amount,
            currency=card.currency,
            merchant_name=merchant,
            description=f'Compra en {merchant}',
        )

        return Response({
            'message': 'Compra exitosa',
            'transaction': VirtualCardTransactionSerializer(tx).data,
            'card_balance': str(card.balance),
        })


# ==============================================================
# REWARDS
# ==============================================================

class MyRewardsView(APIView):
    """Get user's reward points."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rp, _ = RewardPoints.objects.get_or_create(user=request.user)
        return Response(RewardPointsSerializer(rp).data)


class RewardHistoryView(generics.ListAPIView):
    """List user's reward transactions."""
    serializer_class = RewardTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RewardTransaction.objects.filter(user=self.request.user)


class RedeemPointsView(APIView):
    """Redeem points for COP balance (100 points = $1000 COP)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        points = int(request.data.get('points', 0))
        if points < 100:
            return Response({'detail': 'Minimo 100 puntos'}, status=400)

        rp, _ = RewardPoints.objects.get_or_create(user=request.user)
        if rp.balance < points:
            return Response({'detail': 'Puntos insuficientes'}, status=400)

        cop_value = Decimal(points * 10)  # 1 point = 10 COP

        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            wallet.balance_cop += cop_value
            wallet.save()

            rp.balance -= points
            rp.lifetime_redeemed += points
            rp.save()

            RewardTransaction.objects.create(
                user=request.user,
                points=-points,
                transaction_type=RewardTransaction.Type.REDEEMED,
                reason=f'Canje por {cop_value} COP',
            )

            WalletTx.objects.create(
                wallet=wallet,
                transaction_type=WalletTx.TransactionType.DEPOSIT,
                amount=cop_value,
                currency='COP',
                balance_after=wallet.balance_cop,
                reference=f'REWARD-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                description=f'Canje de {points} puntos SuperNova',
                status=WalletTx.Status.COMPLETED,
            )

        return Response({
            'message': f'Has canjeado {points} puntos por ${cop_value} COP',
            'new_balance': str(rp.balance),
        })


# ==============================================================
# WALLET TOP-UP
# ==============================================================

class WalletTopupCreateView(generics.ListCreateAPIView):
    """Create or list wallet top-ups."""
    serializer_class = WalletTopupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WalletTopup.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        topup = serializer.save(
            user=request.user,
            reference=f'TOPUP-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        )

        # In production, this would integrate with payment gateway
        # For now, auto-complete the top-up
        topup.complete()

        return Response(WalletTopupSerializer(topup).data, status=status.HTTP_201_CREATED)
