from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.db import models


class CryptoDeposit(models.Model):
    """Deposito de criptomonedas hacia la billetera LlanoPay."""

    class Currency(models.TextChoices):
        USDT = 'USDT', 'Tether (USDT)'
        ETH = 'ETH', 'Ethereum (ETH)'
        BTC = 'BTC', 'Bitcoin (BTC)'

    class Network(models.TextChoices):
        POLYGON = 'POLYGON', 'Polygon'
        ETHEREUM = 'ETHEREUM', 'Ethereum'
        BSC = 'BSC', 'Binance Smart Chain'
        BITCOIN = 'BITCOIN', 'Bitcoin'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        CONFIRMING = 'CONFIRMING', 'Confirmando'
        CONFIRMED = 'CONFIRMED', 'Confirmado'
        FAILED = 'FAILED', 'Fallido'
        CREDITED = 'CREDITED', 'Acreditado'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='crypto_deposits',
        verbose_name='Usuario',
    )
    currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        verbose_name='Criptomoneda',
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        verbose_name='Cantidad',
    )
    tx_hash = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Hash de transaccion',
    )
    network = models.CharField(
        max_length=20,
        choices=Network.choices,
        verbose_name='Red',
    )
    cop_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Monto en COP',
    )
    exchange_rate = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Tasa de cambio',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado',
    )
    confirmations = models.PositiveIntegerField(
        default=0,
        verbose_name='Confirmaciones',
    )
    required_confirmations = models.PositiveIntegerField(
        default=12,
        verbose_name='Confirmaciones requeridas',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creacion',
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de confirmacion',
    )
    credited_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de acreditacion',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Deposito Crypto'
        verbose_name_plural = 'Depositos Crypto'

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} ({self.status})"


class CryptoWithdrawal(models.Model):
    """Retiro de criptomonedas desde la billetera LlanoPay."""

    class Currency(models.TextChoices):
        USDT = 'USDT', 'Tether (USDT)'
        ETH = 'ETH', 'Ethereum (ETH)'
        BTC = 'BTC', 'Bitcoin (BTC)'

    class Network(models.TextChoices):
        POLYGON = 'POLYGON', 'Polygon'
        ETHEREUM = 'ETHEREUM', 'Ethereum'
        BSC = 'BSC', 'Binance Smart Chain'
        BITCOIN = 'BITCOIN', 'Bitcoin'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PROCESSING = 'PROCESSING', 'Procesando'
        COMPLETED = 'COMPLETED', 'Completado'
        FAILED = 'FAILED', 'Fallido'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='crypto_withdrawals',
        verbose_name='Usuario',
    )
    currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        verbose_name='Criptomoneda',
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        verbose_name='Cantidad',
    )
    destination_address = models.CharField(
        max_length=255,
        verbose_name='Direccion destino',
    )
    tx_hash = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Hash de transaccion',
    )
    network = models.CharField(
        max_length=20,
        choices=Network.choices,
        verbose_name='Red',
    )
    cop_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Monto en COP',
    )
    exchange_rate = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Tasa de cambio',
    )
    fee_amount = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=Decimal('0'),
        verbose_name='Comision',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creacion',
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de procesamiento',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Retiro Crypto'
        verbose_name_plural = 'Retiros Crypto'

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} -> {self.destination_address}"


class ExchangeRate(models.Model):
    """Tasa de cambio cripto a COP, actualizada periodicamente."""

    class Currency(models.TextChoices):
        USDT = 'USDT', 'Tether (USDT)'
        ETH = 'ETH', 'Ethereum (ETH)'
        BTC = 'BTC', 'Bitcoin (BTC)'
        LLO = 'LLO', 'Llanocoin (LLO)'

    currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        unique=True,
        verbose_name='Criptomoneda',
    )
    rate_cop = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name='Tasa en COP',
    )
    source = models.CharField(
        max_length=100,
        verbose_name='Fuente',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Ultima actualizacion',
    )

    class Meta:
        verbose_name = 'Tasa de Cambio'
        verbose_name_plural = 'Tasas de Cambio'

    def __str__(self):
        return f"{self.currency}: {self.rate_cop} COP"

    @classmethod
    def get_rate(cls, currency: str) -> Decimal:
        """Retorna la tasa de cambio para una moneda, con cache de 5 minutos."""
        cache_key = f'exchange_rate_{currency}'
        rate = cache.get(cache_key)
        if rate is not None:
            return Decimal(str(rate))

        try:
            obj = cls.objects.get(currency=currency)
            rate = obj.rate_cop
            cache.set(cache_key, str(rate), timeout=300)
            return rate
        except cls.DoesNotExist:
            if currency == 'LLO':
                return Decimal(str(settings.LLO_COP_RATE))
            return Decimal('0')


class LlanocoinTransaction(models.Model):
    """Transacciones de Llanocoin (LLO) - token interno de LlanoPay."""

    class TransactionType(models.TextChoices):
        BUY = 'BUY', 'Compra'
        SELL = 'SELL', 'Venta'
        TRANSFER_IN = 'TRANSFER_IN', 'Transferencia recibida'
        TRANSFER_OUT = 'TRANSFER_OUT', 'Transferencia enviada'
        REWARD = 'REWARD', 'Recompensa'
        STAKE = 'STAKE', 'Staking'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        COMPLETED = 'COMPLETED', 'Completado'
        FAILED = 'FAILED', 'Fallido'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='llanocoin_transactions',
        verbose_name='Usuario',
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        verbose_name='Tipo de transaccion',
    )
    amount_llo = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        verbose_name='Cantidad LLO',
    )
    amount_cop = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name='Monto COP',
    )
    rate = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('1000'),
        verbose_name='Tasa LLO/COP',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado',
    )
    tx_hash = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Hash de transaccion',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creacion',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transaccion Llanocoin'
        verbose_name_plural = 'Transacciones Llanocoin'

    def __str__(self):
        return f"{self.user} - {self.transaction_type} {self.amount_llo} LLO"
