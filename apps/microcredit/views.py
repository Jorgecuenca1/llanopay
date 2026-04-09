from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.microcredit.models import (
    CreditProfile,
    Microcredit,
    MicrocreditPayment,
    MicrocreditProduct,
)
from apps.microcredit.serializers import (
    CreditProfileSerializer,
    CreditScoreSerializer,
    MicrocreditDetailSerializer,
    MicrocreditPaymentSerializer,
    MicrocreditProductSerializer,
    MicrocreditRequestSerializer,
)


class CreditProfileView(generics.RetrieveAPIView):
    """GET - Obtener el perfil crediticio del usuario autenticado."""

    serializer_class = CreditProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _created = CreditProfile.objects.get_or_create(
            user=self.request.user,
        )
        return profile


class MicrocreditProductListView(generics.ListAPIView):
    """GET - Listar productos de microcredito disponibles."""

    serializer_class = MicrocreditProductSerializer
    permission_classes = [IsAuthenticated]
    queryset = MicrocreditProduct.objects.filter(is_active=True)


class MicrocreditRequestView(APIView):
    """POST - Solicitar un microcredito."""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = MicrocreditRequestSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product']
        credit_profile = serializer.validated_data['credit_profile']
        amount = serializer.validated_data['amount_requested']

        # Calcular colateral LLO si aplica
        llo_collateral = Decimal('0')
        if product.requires_llo_collateral:
            llo_collateral = amount * (product.llo_collateral_percentage / Decimal('100'))

        # Crear el microcredito
        microcredit = Microcredit.objects.create(
            user=request.user,
            product=product,
            amount_requested=amount,
            interest_rate=product.interest_rate_monthly,
            term_days=product.term_days,
            llo_collateral_amount=llo_collateral,
            total_to_repay=Decimal('0'),  # Se calcula al aprobar
        )

        # Calcular total a pagar
        microcredit.amount_approved = amount
        microcredit.calculate_total_to_repay()
        microcredit.save(update_fields=['amount_approved', 'total_to_repay'])

        # Actualizar perfil crediticio
        credit_profile.total_loans = Microcredit.objects.filter(
            user=request.user,
        ).count()
        credit_profile.active_loans = Microcredit.objects.filter(
            user=request.user,
            status__in=[
                Microcredit.Status.REQUESTED,
                Microcredit.Status.APPROVED,
                Microcredit.Status.DISBURSED,
                Microcredit.Status.ACTIVE,
            ],
        ).count()
        credit_profile.save(update_fields=['total_loans', 'active_loans', 'updated_at'])

        detail_serializer = MicrocreditDetailSerializer(microcredit)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


class MicrocreditListView(generics.ListAPIView):
    """GET - Listar los microcreditos del usuario autenticado."""

    serializer_class = MicrocreditDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Microcredit.objects.filter(user=self.request.user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.select_related('product')


class MicrocreditDetailView(generics.RetrieveAPIView):
    """GET - Obtener detalle de un microcredito especifico del usuario."""

    serializer_class = MicrocreditDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Microcredit.objects.filter(
            user=self.request.user,
        ).select_related('product')


class MicrocreditPaymentView(APIView):
    """POST - Realizar un pago a un microcredito de forma atomica."""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = MicrocreditPaymentSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        microcredit = serializer.validated_data['microcredit']
        amount = serializer.validated_data['amount']

        # Bloquear el microcredito para actualizacion atomica
        microcredit = Microcredit.objects.select_for_update().get(pk=microcredit.pk)

        # Determinar tipo de pago
        remaining = microcredit.remaining_balance
        if amount >= remaining:
            payment_type = MicrocreditPayment.PaymentType.EARLY
        elif microcredit.is_overdue:
            payment_type = MicrocreditPayment.PaymentType.LATE_FEE
        elif amount < remaining:
            payment_type = MicrocreditPayment.PaymentType.PARTIAL
        else:
            payment_type = MicrocreditPayment.PaymentType.REGULAR

        # Crear el registro de pago
        payment = MicrocreditPayment.objects.create(
            microcredit=microcredit,
            amount=amount,
            payment_type=payment_type,
            status=MicrocreditPayment.Status.COMPLETED,
            completed_at=timezone.now(),
        )

        # Actualizar el microcredito
        microcredit.amount_repaid = microcredit.amount_repaid + amount
        update_fields = ['amount_repaid']

        # Verificar si se pago el total
        if microcredit.amount_repaid >= microcredit.total_to_repay:
            microcredit.status = Microcredit.Status.PAID
            microcredit.paid_at = timezone.now()
            update_fields.extend(['status', 'paid_at'])

        microcredit.save(update_fields=update_fields)

        # Actualizar perfil crediticio
        credit_profile, _created = CreditProfile.objects.get_or_create(
            user=request.user,
        )
        credit_profile.total_repaid = credit_profile.total_repaid + amount

        if microcredit.is_overdue:
            credit_profile.late_payments = credit_profile.late_payments + 1
        else:
            credit_profile.on_time_payments = credit_profile.on_time_payments + 1

        profile_update_fields = ['total_repaid', 'on_time_payments', 'late_payments', 'updated_at']

        # Si el credito se pago completo, actualizar prestamos activos
        if microcredit.status == Microcredit.Status.PAID:
            credit_profile.active_loans = Microcredit.objects.filter(
                user=request.user,
                status__in=[
                    Microcredit.Status.REQUESTED,
                    Microcredit.Status.APPROVED,
                    Microcredit.Status.DISBURSED,
                    Microcredit.Status.ACTIVE,
                ],
            ).count()
            profile_update_fields.append('active_loans')

        credit_profile.save(update_fields=profile_update_fields)

        return Response({
            'payment_id': str(payment.id),
            'amount_paid': str(amount),
            'payment_type': payment.get_payment_type_display(),
            'remaining_balance': str(microcredit.remaining_balance),
            'microcredit_status': microcredit.get_status_display(),
        }, status=status.HTTP_201_CREATED)


class CreditScoreRecalculateView(APIView):
    """POST - Recalcular el puntaje crediticio del usuario."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile, _created = CreditProfile.objects.get_or_create(
            user=request.user,
        )
        new_score = profile.calculate_score()
        serializer = CreditScoreSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
