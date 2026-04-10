"""
SuperNova Global Features Models.

Contains models for international/global functionality:
- Multi-currency support with exchange rates
- Country profiles
- QR Payments
- Mobile top-ups
- Bill payments
- Referral program
- Virtual cards
- Cashback / rewards
- Wallet top-ups (recharge from external sources)
"""
import secrets
import string
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


# ==============================================================
# COUNTRIES & CURRENCIES
# ==============================================================

class Country(models.Model):
    """ISO 3166 country with phone code and default currency."""
    code = models.CharField(max_length=2, primary_key=True, help_text='ISO 3166-1 alpha-2')
    code3 = models.CharField(max_length=3, blank=True, default='', help_text='ISO 3166-1 alpha-3')
    name = models.CharField(max_length=100)
    name_es = models.CharField(max_length=100, blank=True, default='')
    flag_emoji = models.CharField(max_length=8, blank=True, default='')
    phone_code = models.CharField(max_length=8, blank=True, default='')
    default_currency = models.CharField(max_length=3, default='USD')
    is_supported = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'country'
        verbose_name_plural = 'countries'

    def __str__(self):
        return f'{self.flag_emoji} {self.name}'


class Currency(models.Model):
    """Currency with exchange rates and metadata."""
    code = models.CharField(max_length=3, primary_key=True, help_text='ISO 4217')
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=8, default='$')
    decimal_places = models.PositiveSmallIntegerField(default=2)
    is_crypto = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # Rate relative to USD (1 USD = rate_to_usd in this currency)
    rate_to_usd = models.DecimalField(
        max_digits=20, decimal_places=8,
        default=Decimal('1.0'),
        help_text='How many of this currency = 1 USD',
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name_plural = 'currencies'

    def __str__(self):
        return f'{self.code} ({self.symbol})'

    def to_usd(self, amount):
        """Convert amount of this currency to USD."""
        if self.rate_to_usd == 0:
            return Decimal('0')
        return (Decimal(str(amount)) / self.rate_to_usd).quantize(Decimal('0.01'))

    def from_usd(self, usd_amount):
        """Convert USD to this currency."""
        return (Decimal(str(usd_amount)) * self.rate_to_usd).quantize(Decimal('0.01'))


class MultiBalance(models.Model):
    """Per-currency balance for a user (in addition to main wallet)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='multi_balances',
    )
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    balance = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('user', 'currency')]
        verbose_name = 'multi-currency balance'
        verbose_name_plural = 'multi-currency balances'

    def __str__(self):
        return f'{self.user} - {self.currency.code} {self.balance}'


# ==============================================================
# QR PAYMENTS
# ==============================================================

def gen_qr_code():
    return 'QR-' + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))


class QRPayment(models.Model):
    """QR-based payment requests. User generates QR, others scan and pay."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        EXPIRED = 'EXPIRED', 'Expired'
        CANCELLED = 'CANCELLED', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, default=gen_qr_code)
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='qr_payments_received',
    )
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='qr_payments_made',
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                  help_text='Optional fixed amount; if null, payer enters amount')
    currency = models.CharField(max_length=3, default='COP')
    description = models.CharField(max_length=200, blank=True, default='')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'QR {self.code} - {self.currency} {self.amount or "open"}'


# ==============================================================
# MOBILE TOP-UPS (RECARGAS)
# ==============================================================

class MobileTopup(models.Model):
    """Mobile phone top-up record."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mobile_topups',
    )
    phone_number = models.CharField(max_length=20)
    country_code = models.CharField(max_length=2, default='CO')
    operator = models.CharField(max_length=50, blank=True, default='', help_text='Movistar, Claro, etc')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='COP')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reference = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Topup {self.phone_number} - {self.currency} {self.amount}'


# ==============================================================
# BILL PAYMENTS
# ==============================================================

class BillPayment(models.Model):
    """Utility / service bill payments."""

    class Category(models.TextChoices):
        ELECTRICITY = 'ELECTRICITY', 'Electricity'
        WATER = 'WATER', 'Water'
        GAS = 'GAS', 'Gas'
        INTERNET = 'INTERNET', 'Internet'
        TV = 'TV', 'Cable / Streaming'
        PHONE = 'PHONE', 'Phone'
        TAXES = 'TAXES', 'Taxes'
        EDUCATION = 'EDUCATION', 'Education'
        INSURANCE = 'INSURANCE', 'Insurance'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bill_payments',
    )
    category = models.CharField(max_length=20, choices=Category.choices)
    company = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='COP')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reference = models.CharField(max_length=100, blank=True, default='')
    description = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_category_display()} - {self.company} - {self.amount}'


# ==============================================================
# REFERRAL PROGRAM
# ==============================================================

def gen_referral_code():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))


class ReferralCode(models.Model):
    """Each user gets a unique referral code."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referral_code',
    )
    code = models.CharField(max_length=10, unique=True, default=gen_referral_code)
    total_referrals = models.PositiveIntegerField(default=0)
    total_earned = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.code} ({self.total_referrals})'


class Referral(models.Model):
    """Records when a user is referred by another."""
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referrals_made',
    )
    referred = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referred_by',
    )
    bonus_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    bonus_currency = models.CharField(max_length=3, default='USD')
    bonus_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.referrer} -> {self.referred}'


# ==============================================================
# VIRTUAL CARDS
# ==============================================================

def gen_card_number():
    return '4242' + ''.join(secrets.choice(string.digits) for _ in range(12))


def gen_cvv():
    return ''.join(secrets.choice(string.digits) for _ in range(3))


class VirtualCard(models.Model):
    """Virtual debit card linked to user wallet."""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        FROZEN = 'FROZEN', 'Frozen'
        CANCELLED = 'CANCELLED', 'Cancelled'
        EXPIRED = 'EXPIRED', 'Expired'

    class CardType(models.TextChoices):
        VIRTUAL = 'VIRTUAL', 'Virtual'
        PHYSICAL = 'PHYSICAL', 'Physical'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='virtual_cards',
    )
    card_number = models.CharField(max_length=16, unique=True, default=gen_card_number)
    card_holder_name = models.CharField(max_length=100)
    expiry_month = models.PositiveSmallIntegerField()
    expiry_year = models.PositiveSmallIntegerField()
    cvv = models.CharField(max_length=4, default=gen_cvv)
    card_type = models.CharField(max_length=20, choices=CardType.choices, default=CardType.VIRTUAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    currency = models.CharField(max_length=3, default='USD')
    spending_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('1000'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'**** {self.card_number[-4:]} - {self.user}'

    @property
    def masked_number(self):
        return f'**** **** **** {self.card_number[-4:]}'


# ==============================================================
# CASHBACK / REWARDS
# ==============================================================

class RewardPoints(models.Model):
    """User reward points balance."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reward_points',
    )
    balance = models.PositiveIntegerField(default=0)
    lifetime_earned = models.PositiveIntegerField(default=0)
    lifetime_redeemed = models.PositiveIntegerField(default=0)
    tier = models.CharField(
        max_length=20,
        choices=[
            ('BRONZE', 'Bronze'),
            ('SILVER', 'Silver'),
            ('GOLD', 'Gold'),
            ('PLATINUM', 'Platinum'),
        ],
        default='BRONZE',
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.balance} pts ({self.tier})'

    def add_points(self, points, reason=''):
        self.balance += points
        self.lifetime_earned += points
        self._update_tier()
        self.save()
        RewardTransaction.objects.create(
            user=self.user,
            points=points,
            transaction_type=RewardTransaction.Type.EARNED,
            reason=reason,
        )

    def _update_tier(self):
        if self.lifetime_earned >= 100000:
            self.tier = 'PLATINUM'
        elif self.lifetime_earned >= 25000:
            self.tier = 'GOLD'
        elif self.lifetime_earned >= 5000:
            self.tier = 'SILVER'
        else:
            self.tier = 'BRONZE'


class RewardTransaction(models.Model):
    """Record of points earned or redeemed."""

    class Type(models.TextChoices):
        EARNED = 'EARNED', 'Earned'
        REDEEMED = 'REDEEMED', 'Redeemed'
        EXPIRED = 'EXPIRED', 'Expired'
        BONUS = 'BONUS', 'Bonus'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reward_transactions',
    )
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=Type.choices)
    reason = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.points} {self.transaction_type}'


# ==============================================================
# WALLET TOP-UP (External funding)
# ==============================================================

class WalletTopup(models.Model):
    """Top-up wallet from external source (card, bank, etc)."""

    class Method(models.TextChoices):
        CARD = 'CARD', 'Credit/Debit Card'
        BANK = 'BANK', 'Bank Transfer'
        CASH = 'CASH', 'Cash Deposit'
        CRYPTO = 'CRYPTO', 'Cryptocurrency'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet_topups',
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='COP')
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CARD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reference = models.CharField(max_length=100, blank=True, default='')
    description = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Topup {self.user} - {self.currency} {self.amount} ({self.status})'

    @transaction.atomic
    def complete(self):
        """Credit the user's wallet and mark as completed."""
        from apps.wallet.models import Wallet, Transaction as WTx
        from decimal import Decimal as D

        if self.status == self.Status.COMPLETED:
            return

        wallet, _ = Wallet.objects.get_or_create(user=self.user)
        if self.currency == 'COP':
            wallet.balance_cop = (wallet.balance_cop or D('0')) + self.amount
            wallet.save(update_fields=['balance_cop', 'updated_at'])
        elif self.currency == 'LLO':
            wallet.balance_llo = (wallet.balance_llo or D('0')) + self.amount
            wallet.save(update_fields=['balance_llo', 'updated_at'])

        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

        # Create transaction record
        WTx.objects.create(
            wallet=wallet,
            transaction_type=WTx.TransactionType.DEPOSIT,
            amount=self.amount,
            currency=self.currency if self.currency in ['COP', 'LLO'] else 'COP',
            balance_after=wallet.balance_cop if self.currency == 'COP' else wallet.balance_llo,
            reference=str(self.id),
            description=f'Recarga via {self.get_method_display()}',
            status=WTx.Status.COMPLETED,
            metadata={'topup_id': str(self.id), 'method': self.method},
        )

        # Award reward points (1 point per 1000 COP, or equivalent)
        try:
            from apps.global_features.models import RewardPoints
            rp, _ = RewardPoints.objects.get_or_create(user=self.user)
            points = int(float(self.amount) / 1000) if self.currency == 'COP' else int(float(self.amount) * 4)
            if points > 0:
                rp.add_points(points, f'Recarga {self.currency} {self.amount}')
        except Exception:
            pass
