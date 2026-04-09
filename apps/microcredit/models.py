import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import F, Sum
from django.utils import timezone


class CreditProfile(models.Model):
    """Perfil crediticio del usuario basado en historial de uso y comportamiento."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_profile',
        verbose_name='usuario',
    )
    credit_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        verbose_name='puntaje crediticio',
        help_text='Puntaje de 0 a 1000 basado en comportamiento de pagos.',
    )
    max_credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='monto maximo de credito',
    )
    total_loans = models.IntegerField(
        default=0,
        verbose_name='total de prestamos',
    )
    active_loans = models.IntegerField(
        default=0,
        verbose_name='prestamos activos',
    )
    total_repaid = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='total pagado',
    )
    on_time_payments = models.IntegerField(
        default=0,
        verbose_name='pagos a tiempo',
    )
    late_payments = models.IntegerField(
        default=0,
        verbose_name='pagos tardios',
    )
    last_evaluated_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='ultima evaluacion',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='fecha de actualizacion')

    class Meta:
        verbose_name = 'perfil crediticio'
        verbose_name_plural = 'perfiles crediticios'

    def __str__(self):
        return f'Perfil crediticio de {self.user} - Score: {self.credit_score}'

    def calculate_score(self):
        """Calcular puntaje crediticio basado en historial de transacciones y pagos.

        Factores:
        - Historial de pagos (40%): pagos a tiempo vs tardios.
        - Cantidad de prestamos completados (20%): mas prestamos pagados = mejor.
        - Monto total pagado (15%): volumen de pagos realizados.
        - Antiguedad de la cuenta (15%): mas tiempo = mas confiable.
        - Prestamos activos (10%): menos prestamos activos = menor riesgo.
        """
        score = Decimal('0')

        # Factor 1: Historial de pagos (40% = 400 puntos max)
        total_payments = self.on_time_payments + self.late_payments
        if total_payments > 0:
            on_time_ratio = Decimal(self.on_time_payments) / Decimal(total_payments)
            score += on_time_ratio * 400
        else:
            # Sin historial de pagos, puntaje base
            score += 100

        # Factor 2: Prestamos completados (20% = 200 puntos max)
        completed_loans = Microcredit.objects.filter(
            user=self.user,
            status=Microcredit.Status.PAID,
        ).count()
        loan_score = min(completed_loans * 40, 200)
        score += loan_score

        # Factor 3: Monto total pagado (15% = 150 puntos max)
        if self.total_repaid > 0:
            repaid_tiers = [
                (Decimal('5000000'), 150),
                (Decimal('2000000'), 120),
                (Decimal('1000000'), 90),
                (Decimal('500000'), 60),
                (Decimal('100000'), 30),
            ]
            for threshold, points in repaid_tiers:
                if self.total_repaid >= threshold:
                    score += points
                    break

        # Factor 4: Antiguedad de la cuenta (15% = 150 puntos max)
        account_age_days = (timezone.now() - self.created_at).days
        age_score = min(account_age_days // 30 * 15, 150)  # 15 puntos por mes, max 150
        score += age_score

        # Factor 5: Prestamos activos (10% = 100 puntos max)
        if self.active_loans == 0:
            score += 100
        elif self.active_loans == 1:
            score += 60
        elif self.active_loans == 2:
            score += 30
        # Mas de 2 prestamos activos = 0 puntos en este factor

        # Penalizacion por prestamos en mora
        defaulted_count = Microcredit.objects.filter(
            user=self.user,
            status=Microcredit.Status.DEFAULTED,
        ).count()
        score -= defaulted_count * 100

        # Asegurar rango 0-1000
        final_score = max(0, min(1000, int(score)))
        self.credit_score = final_score

        # Calcular monto maximo basado en el score
        if final_score >= 800:
            self.max_credit_amount = Decimal('5000000')
        elif final_score >= 600:
            self.max_credit_amount = Decimal('3000000')
        elif final_score >= 400:
            self.max_credit_amount = Decimal('1500000')
        elif final_score >= 200:
            self.max_credit_amount = Decimal('500000')
        elif final_score >= 100:
            self.max_credit_amount = Decimal('200000')
        else:
            self.max_credit_amount = Decimal('0')

        self.last_evaluated_at = timezone.now()
        self.save(update_fields=[
            'credit_score',
            'max_credit_amount',
            'last_evaluated_at',
            'updated_at',
        ])
        return final_score


class MicrocreditProduct(models.Model):
    """Producto de microcredito disponible en la plataforma.

    Ejemplos: Credito Campesino, Credito Comerciante.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        verbose_name='nombre',
        help_text='Ej: Credito Campesino, Credito Comerciante',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='descripcion',
    )
    min_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='monto minimo',
    )
    max_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='monto maximo',
    )
    interest_rate_monthly = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='tasa de interes mensual (%)',
        help_text='Porcentaje mensual de interes. Ej: 2.5 = 2.5%',
    )
    term_days = models.IntegerField(
        verbose_name='plazo en dias',
        help_text='Plazo maximo del credito en dias.',
    )
    grace_period_days = models.IntegerField(
        default=0,
        verbose_name='dias de gracia',
        help_text='Dias de gracia antes de iniciar cobro de intereses.',
    )
    requires_llo_collateral = models.BooleanField(
        default=False,
        verbose_name='requiere colateral en LLO',
    )
    llo_collateral_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='porcentaje de colateral LLO',
        help_text='Porcentaje del monto que se requiere en LLO como colateral.',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='activo',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='fecha de actualizacion')

    class Meta:
        verbose_name = 'producto de microcredito'
        verbose_name_plural = 'productos de microcredito'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.interest_rate_monthly}% mensual)'

    def clean(self):
        if self.min_amount and self.max_amount and self.min_amount > self.max_amount:
            raise ValidationError({
                'min_amount': 'El monto minimo no puede ser mayor al monto maximo.',
            })


class Microcredit(models.Model):
    """Microcredito digital solicitado por un usuario."""

    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Solicitado'
        APPROVED = 'APPROVED', 'Aprobado'
        DISBURSED = 'DISBURSED', 'Desembolsado'
        ACTIVE = 'ACTIVE', 'Activo'
        PAID = 'PAID', 'Pagado'
        DEFAULTED = 'DEFAULTED', 'En mora'
        REJECTED = 'REJECTED', 'Rechazado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='microcredits',
        verbose_name='usuario',
    )
    product = models.ForeignKey(
        MicrocreditProduct,
        on_delete=models.PROTECT,
        related_name='microcredits',
        verbose_name='producto',
    )
    amount_requested = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='monto solicitado',
    )
    amount_approved = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='monto aprobado',
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='tasa de interes (%)',
    )
    term_days = models.IntegerField(
        verbose_name='plazo en dias',
    )
    llo_collateral_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='monto colateral LLO',
    )
    total_to_repay = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='total a pagar',
    )
    amount_repaid = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='monto pagado',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.REQUESTED,
        verbose_name='estado',
    )
    disbursed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='fecha de desembolso',
    )
    due_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='fecha de vencimiento',
    )
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='fecha de pago completo',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')

    class Meta:
        verbose_name = 'microcredito'
        verbose_name_plural = 'microcreditos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_microcredit_user_status'),
            models.Index(fields=['due_date', 'status'], name='idx_microcredit_due_status'),
        ]

    def __str__(self):
        return (
            f'Microcredito {self.id} - {self.user} - '
            f'${self.amount_requested} ({self.get_status_display()})'
        )

    @property
    def remaining_balance(self):
        """Saldo pendiente por pagar."""
        return self.total_to_repay - self.amount_repaid

    @property
    def is_overdue(self):
        """Indica si el credito esta vencido."""
        if self.due_date and self.status in (self.Status.ACTIVE, self.Status.DISBURSED):
            return timezone.now() > self.due_date
        return False

    def calculate_total_to_repay(self):
        """Calcular el total a pagar incluyendo intereses."""
        amount = self.amount_approved or self.amount_requested
        months = Decimal(self.term_days) / Decimal('30')
        interest = amount * (self.interest_rate / Decimal('100')) * months
        self.total_to_repay = amount + interest
        return self.total_to_repay


class MicrocreditPayment(models.Model):
    """Registro de pagos realizados a un microcredito."""

    class PaymentType(models.TextChoices):
        REGULAR = 'REGULAR', 'Pago regular'
        EARLY = 'EARLY', 'Pago anticipado'
        PARTIAL = 'PARTIAL', 'Abono parcial'
        LATE_FEE = 'LATE_FEE', 'Recargo por mora'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        COMPLETED = 'COMPLETED', 'Completado'
        FAILED = 'FAILED', 'Fallido'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    microcredit = models.ForeignKey(
        Microcredit,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='microcredito',
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='monto',
    )
    payment_type = models.CharField(
        max_length=10,
        choices=PaymentType.choices,
        default=PaymentType.REGULAR,
        verbose_name='tipo de pago',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='estado',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='fecha de completado',
    )

    class Meta:
        verbose_name = 'pago de microcredito'
        verbose_name_plural = 'pagos de microcredito'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'Pago ${self.amount} - Credito {self.microcredit_id} '
            f'({self.get_status_display()})'
        )
