import uuid

from django.conf import settings
from django.db import models, transaction
from django.db.models import F
from django.core.exceptions import ValidationError


class Wallet(models.Model):
    """Billetera digital del usuario con saldos en COP y LLO."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name='usuario',
    )
    balance_cop = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='saldo COP',
    )
    balance_llo = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='saldo LLO',
    )
    is_active = models.BooleanField(default=True, verbose_name='activa')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='fecha de actualizacion')

    class Meta:
        verbose_name = 'billetera'
        verbose_name_plural = 'billeteras'

    def __str__(self):
        return f'Billetera de {self.user} - COP {self.balance_cop} / LLO {self.balance_llo}'

    @transaction.atomic
    def deposit_cop(self, amount):
        """Depositar pesos colombianos de forma atomica."""
        if amount <= 0:
            raise ValidationError('El monto del deposito debe ser positivo.')
        wallet = Wallet.objects.select_for_update().get(pk=self.pk)
        wallet.balance_cop = F('balance_cop') + amount
        wallet.save(update_fields=['balance_cop', 'updated_at'])
        wallet.refresh_from_db()
        self.balance_cop = wallet.balance_cop
        return self.balance_cop

    @transaction.atomic
    def withdraw_cop(self, amount):
        """Retirar pesos colombianos de forma atomica."""
        if amount <= 0:
            raise ValidationError('El monto del retiro debe ser positivo.')
        wallet = Wallet.objects.select_for_update().get(pk=self.pk)
        if wallet.balance_cop < amount:
            raise ValidationError('Saldo COP insuficiente.')
        wallet.balance_cop = F('balance_cop') - amount
        wallet.save(update_fields=['balance_cop', 'updated_at'])
        wallet.refresh_from_db()
        self.balance_cop = wallet.balance_cop
        return self.balance_cop

    @transaction.atomic
    def deposit_llo(self, amount):
        """Depositar LlanoCoins de forma atomica."""
        if amount <= 0:
            raise ValidationError('El monto del deposito debe ser positivo.')
        wallet = Wallet.objects.select_for_update().get(pk=self.pk)
        wallet.balance_llo = F('balance_llo') + amount
        wallet.save(update_fields=['balance_llo', 'updated_at'])
        wallet.refresh_from_db()
        self.balance_llo = wallet.balance_llo
        return self.balance_llo

    @transaction.atomic
    def withdraw_llo(self, amount):
        """Retirar LlanoCoins de forma atomica."""
        if amount <= 0:
            raise ValidationError('El monto del retiro debe ser positivo.')
        wallet = Wallet.objects.select_for_update().get(pk=self.pk)
        if wallet.balance_llo < amount:
            raise ValidationError('Saldo LLO insuficiente.')
        wallet.balance_llo = F('balance_llo') - amount
        wallet.save(update_fields=['balance_llo', 'updated_at'])
        wallet.refresh_from_db()
        self.balance_llo = wallet.balance_llo
        return self.balance_llo


class Transaction(models.Model):
    """Registro de transacciones de la billetera."""

    class TransactionType(models.TextChoices):
        DEPOSIT = 'DEPOSIT', 'Deposito'
        WITHDRAWAL = 'WITHDRAWAL', 'Retiro'
        TRANSFER_IN = 'TRANSFER_IN', 'Transferencia recibida'
        TRANSFER_OUT = 'TRANSFER_OUT', 'Transferencia enviada'
        CRYPTO_DEPOSIT = 'CRYPTO_DEPOSIT', 'Deposito cripto'
        LLO_PURCHASE = 'LLO_PURCHASE', 'Compra de LLO'
        LLO_SALE = 'LLO_SALE', 'Venta de LLO'
        COMMISSION = 'COMMISSION', 'Comision'
        MICROCREDIT_DISBURSEMENT = 'MICROCREDIT_DISBURSEMENT', 'Desembolso de microcredito'
        MICROCREDIT_PAYMENT = 'MICROCREDIT_PAYMENT', 'Pago de microcredito'

    class Currency(models.TextChoices):
        COP = 'COP', 'Peso colombiano'
        LLO = 'LLO', 'LlanoCoin'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        COMPLETED = 'COMPLETED', 'Completada'
        FAILED = 'FAILED', 'Fallida'
        REVERSED = 'REVERSED', 'Reversada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='billetera',
    )
    transaction_type = models.CharField(
        max_length=25,
        choices=TransactionType.choices,
        verbose_name='tipo de transaccion',
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
    balance_after = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='saldo despues',
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='referencia',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='descripcion',
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='metadatos',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='estado',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')

    class Meta:
        verbose_name = 'transaccion'
        verbose_name_plural = 'transacciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', 'created_at'], name='idx_wallet_created'),
        ]

    def __str__(self):
        return (
            f'{self.get_transaction_type_display()} - '
            f'{self.currency} {self.amount} ({self.get_status_display()})'
        )


class MasterWalletManager(models.Manager):
    """Manager que implementa patron singleton para la billetera maestra."""

    def get_master(self):
        obj, _created = self.get_or_create(pk=1)
        return obj


class MasterWallet(models.Model):
    """Billetera maestra del sistema (singleton). Controla las reservas globales."""

    balance_cop = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='saldo COP',
    )
    balance_llo = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='saldo LLO',
    )
    total_crypto_reserves_usd = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='reservas cripto totales (USD)',
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='fecha de actualizacion')

    objects = MasterWalletManager()

    class Meta:
        verbose_name = 'billetera maestra'
        verbose_name_plural = 'billetera maestra'

    def __str__(self):
        return (
            f'Billetera Maestra - COP {self.balance_cop} / '
            f'LLO {self.balance_llo} / USD {self.total_crypto_reserves_usd}'
        )

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
