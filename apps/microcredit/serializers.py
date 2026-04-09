from decimal import Decimal

from rest_framework import serializers

from apps.microcredit.models import (
    CreditProfile,
    Microcredit,
    MicrocreditPayment,
    MicrocreditProduct,
)


class CreditProfileSerializer(serializers.ModelSerializer):
    payment_reliability = serializers.SerializerMethodField()

    class Meta:
        model = CreditProfile
        fields = [
            'id',
            'credit_score',
            'max_credit_amount',
            'total_loans',
            'active_loans',
            'total_repaid',
            'on_time_payments',
            'late_payments',
            'payment_reliability',
            'last_evaluated_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_payment_reliability(self, obj):
        """Porcentaje de pagos realizados a tiempo."""
        total = obj.on_time_payments + obj.late_payments
        if total == 0:
            return None
        return round(obj.on_time_payments / total * 100, 1)


class CreditScoreSerializer(serializers.Serializer):
    credit_score = serializers.IntegerField(read_only=True)
    max_credit_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True,
    )


class MicrocreditProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = MicrocreditProduct
        fields = [
            'id',
            'name',
            'description',
            'min_amount',
            'max_amount',
            'interest_rate_monthly',
            'term_days',
            'grace_period_days',
            'requires_llo_collateral',
            'llo_collateral_percentage',
            'is_active',
        ]
        read_only_fields = fields


class MicrocreditRequestSerializer(serializers.Serializer):
    """Serializer para solicitar un microcredito."""

    product_id = serializers.UUIDField()
    amount_requested = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('1000'),
    )

    def validate_product_id(self, value):
        try:
            product = MicrocreditProduct.objects.get(pk=value, is_active=True)
        except MicrocreditProduct.DoesNotExist:
            raise serializers.ValidationError(
                'El producto de microcredito no existe o no esta activo.'
            )
        self._product = product
        return value

    def validate(self, attrs):
        product = self._product
        amount = attrs['amount_requested']

        if amount < product.min_amount:
            raise serializers.ValidationError({
                'amount_requested': (
                    f'El monto minimo para este producto es '
                    f'${product.min_amount}.'
                ),
            })

        if amount > product.max_amount:
            raise serializers.ValidationError({
                'amount_requested': (
                    f'El monto maximo para este producto es '
                    f'${product.max_amount}.'
                ),
            })

        # Verificar perfil crediticio del usuario
        user = self.context['request'].user
        credit_profile, _created = CreditProfile.objects.get_or_create(user=user)

        if amount > credit_profile.max_credit_amount:
            raise serializers.ValidationError({
                'amount_requested': (
                    f'Su limite de credito actual es '
                    f'${credit_profile.max_credit_amount}. '
                    f'Solicite un monto menor o mejore su puntaje crediticio.'
                ),
            })

        # Verificar que no tenga demasiados prestamos activos
        active_count = Microcredit.objects.filter(
            user=user,
            status__in=[
                Microcredit.Status.REQUESTED,
                Microcredit.Status.APPROVED,
                Microcredit.Status.DISBURSED,
                Microcredit.Status.ACTIVE,
            ],
        ).count()

        if active_count >= 3:
            raise serializers.ValidationError(
                'Ya tiene el maximo de prestamos activos permitidos (3). '
                'Debe completar un prestamo existente antes de solicitar uno nuevo.'
            )

        attrs['product'] = product
        attrs['credit_profile'] = credit_profile
        return attrs


class MicrocreditDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    remaining_balance = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True,
    )
    is_overdue = serializers.BooleanField(read_only=True)
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Microcredit
        fields = [
            'id',
            'product',
            'product_name',
            'amount_requested',
            'amount_approved',
            'interest_rate',
            'term_days',
            'llo_collateral_amount',
            'total_to_repay',
            'amount_repaid',
            'remaining_balance',
            'status',
            'status_display',
            'is_overdue',
            'disbursed_at',
            'due_date',
            'paid_at',
            'created_at',
            'payments',
        ]
        read_only_fields = fields

    def get_payments(self, obj):
        payments = obj.payments.all().order_by('-created_at')[:10]
        return MicrocreditPaymentDetailSerializer(payments, many=True).data


class MicrocreditPaymentSerializer(serializers.Serializer):
    """Serializer para realizar un pago a un microcredito."""

    microcredit_id = serializers.UUIDField()
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('100'),
    )

    def validate_microcredit_id(self, value):
        user = self.context['request'].user
        try:
            microcredit = Microcredit.objects.get(
                pk=value,
                user=user,
            )
        except Microcredit.DoesNotExist:
            raise serializers.ValidationError(
                'El microcredito no existe o no le pertenece.'
            )

        if microcredit.status not in (
            Microcredit.Status.DISBURSED,
            Microcredit.Status.ACTIVE,
        ):
            raise serializers.ValidationError(
                'Solo se pueden realizar pagos a creditos desembolsados o activos.'
            )

        self._microcredit = microcredit
        return value

    def validate(self, attrs):
        microcredit = self._microcredit
        amount = attrs['amount']
        remaining = microcredit.remaining_balance

        if amount > remaining:
            raise serializers.ValidationError({
                'amount': (
                    f'El monto excede el saldo pendiente de '
                    f'${remaining}.'
                ),
            })

        attrs['microcredit'] = microcredit
        return attrs


class MicrocreditPaymentDetailSerializer(serializers.ModelSerializer):
    payment_type_display = serializers.CharField(
        source='get_payment_type_display', read_only=True,
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )

    class Meta:
        model = MicrocreditPayment
        fields = [
            'id',
            'microcredit',
            'amount',
            'payment_type',
            'payment_type_display',
            'status',
            'status_display',
            'created_at',
            'completed_at',
        ]
        read_only_fields = fields
