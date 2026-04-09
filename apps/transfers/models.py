import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Sum
from django.utils import timezone


class Transfer(models.Model):
    """Transferencia P2P entre usuarios de LlanoPay."""

    class Currency(models.TextChoices):
        COP = 'COP', 'Peso colombiano'
        LLO = 'LLO', 'LlanoCoin'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        OTP_REQUIRED = 'OTP_REQUIRED', 'Requiere OTP'
        COMPLETED = 'COMPLETED', 'Completada'
        FAILED = 'FAILED', 'Fallida'
        REVERSED = 'REVERSED', 'Reversada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_transfers',
        verbose_name='remitente',
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_transfers',
        verbose_name='destinatario',
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='monto',
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        verbose_name='moneda',
    )
    commission_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='monto de comision',
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='tasa de comision',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='descripcion',
    )
    reference = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='referencia',
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='estado',
    )
    otp_verified = models.BooleanField(
        default=False,
        verbose_name='OTP verificado',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de creacion',
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='fecha de completado',
    )

    class Meta:
        verbose_name = 'transferencia'
        verbose_name_plural = 'transferencias'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['sender', 'created_at'],
                name='idx_transfer_sender_created',
            ),
            models.Index(
                fields=['receiver', 'created_at'],
                name='idx_transfer_receiver_created',
            ),
        ]

    def __str__(self):
        return (
            f'Transferencia {self.reference} - '
            f'{self.currency} {self.amount} '
            f'({self.sender} -> {self.receiver})'
        )

    @staticmethod
    def calculate_commission_rate(amount, currency):
        """Calcula la tasa de comision basada en el monto y la moneda.

        Para COP:
          - < 100,000: 0.5%
          - 100,000 - 1,000,000: 1.0%
          - > 1,000,000: 1.5%
        Para LLO se aplica la misma escala usando el equivalente COP.
        """
        if currency == Transfer.Currency.LLO:
            cop_equivalent = amount * Decimal(str(settings.LLO_COP_RATE))
        else:
            cop_equivalent = amount

        if cop_equivalent < Decimal('100000'):
            return Decimal('0.0050')
        elif cop_equivalent <= Decimal('1000000'):
            return Decimal('0.0100')
        else:
            return Decimal('0.0150')

    def calculate_commission(self):
        """Calcula y asigna la comision para esta transferencia."""
        self.commission_rate = self.calculate_commission_rate(
            self.amount, self.currency,
        )
        self.commission_amount = (self.amount * self.commission_rate).quantize(
            Decimal('0.01'),
        )
        return self.commission_amount

    @transaction.atomic
    def execute(self):
        """Ejecuta la transferencia de forma atomica.

        1. Bloquea las billeteras del remitente y destinatario.
        2. Debita al remitente (monto + comision).
        3. Acredita al destinatario (monto).
        4. Registra la comision en la billetera maestra.
        5. Crea registros Transaction para ambas billeteras.
        """
        from apps.wallet.models import Wallet, Transaction as WalletTransaction, MasterWallet

        if self.status not in (self.Status.PENDING, self.Status.OTP_REQUIRED):
            raise ValidationError(
                'Solo se pueden ejecutar transferencias en estado PENDING u OTP_REQUIRED.',
            )

        # Calcular comision si no se ha calculado
        if self.commission_amount == Decimal('0.00'):
            self.calculate_commission()

        total_debit = self.amount + self.commission_amount

        # Bloquear ambas billeteras en orden consistente para evitar deadlocks
        wallet_ids = sorted([self.sender.wallet.pk, self.receiver.wallet.pk])
        wallets = list(
            Wallet.objects.select_for_update().filter(pk__in=wallet_ids)
        )
        wallet_map = {w.pk: w for w in wallets}
        sender_wallet = wallet_map[self.sender.wallet.pk]
        receiver_wallet = wallet_map[self.receiver.wallet.pk]

        # Validar billeteras activas
        if not sender_wallet.is_active:
            self.status = self.Status.FAILED
            self.save(update_fields=['status'])
            raise ValidationError('La billetera del remitente esta inactiva.')

        if not receiver_wallet.is_active:
            self.status = self.Status.FAILED
            self.save(update_fields=['status'])
            raise ValidationError('La billetera del destinatario esta inactiva.')

        # Verificar saldo suficiente
        if self.currency == self.Currency.COP:
            if sender_wallet.balance_cop < total_debit:
                self.status = self.Status.FAILED
                self.save(update_fields=['status'])
                raise ValidationError(
                    f'Saldo COP insuficiente. Se requiere {total_debit}, '
                    f'disponible {sender_wallet.balance_cop}.',
                )
            # Debitar remitente
            sender_wallet.balance_cop = F('balance_cop') - total_debit
            sender_wallet.save(update_fields=['balance_cop', 'updated_at'])
            sender_wallet.refresh_from_db()

            # Acreditar destinatario
            receiver_wallet.balance_cop = F('balance_cop') + self.amount
            receiver_wallet.save(update_fields=['balance_cop', 'updated_at'])
            receiver_wallet.refresh_from_db()

            sender_balance_after = sender_wallet.balance_cop
            receiver_balance_after = receiver_wallet.balance_cop

        else:  # LLO
            if sender_wallet.balance_llo < total_debit:
                self.status = self.Status.FAILED
                self.save(update_fields=['status'])
                raise ValidationError(
                    f'Saldo LLO insuficiente. Se requiere {total_debit}, '
                    f'disponible {sender_wallet.balance_llo}.',
                )
            # Debitar remitente
            sender_wallet.balance_llo = F('balance_llo') - total_debit
            sender_wallet.save(update_fields=['balance_llo', 'updated_at'])
            sender_wallet.refresh_from_db()

            # Acreditar destinatario
            receiver_wallet.balance_llo = F('balance_llo') + self.amount
            receiver_wallet.save(update_fields=['balance_llo', 'updated_at'])
            receiver_wallet.refresh_from_db()

            sender_balance_after = sender_wallet.balance_llo
            receiver_balance_after = receiver_wallet.balance_llo

        # Crear transaccion de salida para el remitente
        WalletTransaction.objects.create(
            wallet=sender_wallet,
            transaction_type=WalletTransaction.TransactionType.TRANSFER_OUT,
            amount=self.amount,
            currency=self.currency,
            balance_after=sender_balance_after,
            reference=str(self.reference),
            description=self.description or f'Transferencia a {self.receiver.phone_number}',
            status=WalletTransaction.Status.COMPLETED,
            metadata={'transfer_id': str(self.pk), 'commission': str(self.commission_amount)},
        )

        # Crear transaccion de entrada para el destinatario
        WalletTransaction.objects.create(
            wallet=receiver_wallet,
            transaction_type=WalletTransaction.TransactionType.TRANSFER_IN,
            amount=self.amount,
            currency=self.currency,
            balance_after=receiver_balance_after,
            reference=str(self.reference),
            description=self.description or f'Transferencia de {self.sender.phone_number}',
            status=WalletTransaction.Status.COMPLETED,
            metadata={'transfer_id': str(self.pk)},
        )

        # Registrar comision en la billetera maestra
        if self.commission_amount > Decimal('0.00'):
            master_wallet = MasterWallet.objects.get_master()
            master_wallet = MasterWallet.objects.select_for_update().get(pk=master_wallet.pk)
            if self.currency == self.Currency.COP:
                master_wallet.balance_cop = F('balance_cop') + self.commission_amount
            else:
                master_wallet.balance_llo = F('balance_llo') + self.commission_amount
            master_wallet.save()

            # Crear transaccion de comision para el remitente
            WalletTransaction.objects.create(
                wallet=sender_wallet,
                transaction_type=WalletTransaction.TransactionType.COMMISSION,
                amount=self.commission_amount,
                currency=self.currency,
                balance_after=sender_balance_after,
                reference=str(self.reference),
                description=f'Comision por transferencia ({self.commission_rate * 100}%)',
                status=WalletTransaction.Status.COMPLETED,
                metadata={'transfer_id': str(self.pk), 'rate': str(self.commission_rate)},
            )

        # Marcar la transferencia como completada
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'commission_amount', 'commission_rate'])

        return self


class TransferLimit(models.Model):
    """Limites de transferencia por usuario."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transfer_limit',
        verbose_name='usuario',
    )
    daily_limit_cop = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('5000000.00'),
        verbose_name='limite diario COP',
    )
    monthly_limit_cop = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('20000000.00'),
        verbose_name='limite mensual COP',
    )
    per_transaction_limit_cop = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('2000000.00'),
        verbose_name='limite por transaccion COP',
    )

    class Meta:
        verbose_name = 'limite de transferencia'
        verbose_name_plural = 'limites de transferencia'

    def __str__(self):
        return f'Limites de {self.user} - Diario: {self.daily_limit_cop}'

    def _get_cop_equivalent(self, amount, currency):
        """Convierte un monto a COP equivalente para validacion de limites."""
        if currency == Transfer.Currency.LLO:
            return amount * Decimal(str(settings.LLO_COP_RATE))
        return amount

    def check_per_transaction(self, amount, currency='COP'):
        """Verifica el limite por transaccion.

        Returns:
            tuple: (bool, str) - (cumple_limite, mensaje_error)
        """
        cop_amount = self._get_cop_equivalent(amount, currency)
        if cop_amount > self.per_transaction_limit_cop:
            return False, (
                f'El monto {cop_amount} COP excede el limite por transaccion '
                f'de {self.per_transaction_limit_cop} COP.'
            )
        return True, ''

    def check_daily_limit(self, amount, currency='COP'):
        """Verifica el limite diario de transferencias.

        Returns:
            tuple: (bool, str) - (cumple_limite, mensaje_error)
        """
        cop_amount = self._get_cop_equivalent(amount, currency)
        today = timezone.now().date()
        daily_total = Transfer.objects.filter(
            sender=self.user,
            status=Transfer.Status.COMPLETED,
            created_at__date=today,
        ).aggregate(
            total=Sum('amount', default=Decimal('0.00')),
        )['total']

        # Convertir el total diario a COP si es necesario
        if daily_total + cop_amount > self.daily_limit_cop:
            remaining = self.daily_limit_cop - daily_total
            return False, (
                f'El monto excede el limite diario. '
                f'Disponible hoy: {remaining} COP de {self.daily_limit_cop} COP.'
            )
        return True, ''

    def check_monthly_limit(self, amount, currency='COP'):
        """Verifica el limite mensual de transferencias.

        Returns:
            tuple: (bool, str) - (cumple_limite, mensaje_error)
        """
        cop_amount = self._get_cop_equivalent(amount, currency)
        now = timezone.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_total = Transfer.objects.filter(
            sender=self.user,
            status=Transfer.Status.COMPLETED,
            created_at__gte=first_day_of_month,
        ).aggregate(
            total=Sum('amount', default=Decimal('0.00')),
        )['total']

        if monthly_total + cop_amount > self.monthly_limit_cop:
            remaining = self.monthly_limit_cop - monthly_total
            return False, (
                f'El monto excede el limite mensual. '
                f'Disponible este mes: {remaining} COP de {self.monthly_limit_cop} COP.'
            )
        return True, ''

    def check_all_limits(self, amount, currency='COP'):
        """Verifica todos los limites. Retorna la primera violacion encontrada.

        Returns:
            tuple: (bool, str) - (cumple_todos, mensaje_error)
        """
        for check in (self.check_per_transaction, self.check_daily_limit, self.check_monthly_limit):
            ok, msg = check(amount, currency)
            if not ok:
                return False, msg
        return True, ''


class ScheduledTransfer(models.Model):
    """Transferencia programada/recurrente entre usuarios."""

    class Frequency(models.TextChoices):
        DAILY = 'DAILY', 'Diaria'
        WEEKLY = 'WEEKLY', 'Semanal'
        BIWEEKLY = 'BIWEEKLY', 'Quincenal'
        MONTHLY = 'MONTHLY', 'Mensual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scheduled_transfers_sent',
        verbose_name='remitente',
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scheduled_transfers_received',
        verbose_name='destinatario',
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='monto',
    )
    currency = models.CharField(
        max_length=3,
        choices=Transfer.Currency.choices,
        verbose_name='moneda',
    )
    frequency = models.CharField(
        max_length=10,
        choices=Frequency.choices,
        verbose_name='frecuencia',
    )
    next_execution_date = models.DateField(
        verbose_name='proxima fecha de ejecucion',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='activa',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='descripcion',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de creacion',
    )

    class Meta:
        verbose_name = 'transferencia programada'
        verbose_name_plural = 'transferencias programadas'
        ordering = ['next_execution_date']

    def __str__(self):
        return (
            f'Programada {self.get_frequency_display()} - '
            f'{self.currency} {self.amount} '
            f'({self.sender} -> {self.receiver})'
        )
