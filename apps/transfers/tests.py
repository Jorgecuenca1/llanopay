from decimal import Decimal
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import User, OTPCode
from apps.transfers.models import Transfer, TransferLimit, ScheduledTransfer
from apps.wallet.models import Wallet, Transaction, MasterWallet


class TransferModelTestMixin:
    """Mixin con helpers para crear usuarios y billeteras de prueba."""

    def create_user(self, phone, balance_cop=Decimal('1000000'), balance_llo=Decimal('500')):
        user = User.objects.create_user(
            phone_number=phone,
            password='testpass123',
            document_type='CC',
            document_number='1234567890',
            first_name='Test',
            last_name='User',
            is_verified=True,
        )
        wallet = Wallet.objects.create(
            user=user,
            balance_cop=balance_cop,
            balance_llo=balance_llo,
        )
        TransferLimit.objects.create(user=user)
        return user


class CommissionCalculationTest(TestCase):
    """Tests para el calculo de comisiones por transferencia."""

    def test_commission_rate_under_100k(self):
        rate = Transfer.calculate_commission_rate(Decimal('50000'), 'COP')
        self.assertEqual(rate, Decimal('0.0050'))

    def test_commission_rate_at_100k(self):
        rate = Transfer.calculate_commission_rate(Decimal('100000'), 'COP')
        self.assertEqual(rate, Decimal('0.0100'))

    def test_commission_rate_between_100k_and_1m(self):
        rate = Transfer.calculate_commission_rate(Decimal('500000'), 'COP')
        self.assertEqual(rate, Decimal('0.0100'))

    def test_commission_rate_at_1m(self):
        rate = Transfer.calculate_commission_rate(Decimal('1000000'), 'COP')
        self.assertEqual(rate, Decimal('0.0100'))

    def test_commission_rate_above_1m(self):
        rate = Transfer.calculate_commission_rate(Decimal('1500000'), 'COP')
        self.assertEqual(rate, Decimal('0.0150'))

    @override_settings(LLO_COP_RATE=1000)
    def test_commission_rate_llo_converts_to_cop(self):
        # 200 LLO * 1000 = 200,000 COP -> 1% rate
        rate = Transfer.calculate_commission_rate(Decimal('200'), 'LLO')
        self.assertEqual(rate, Decimal('0.0100'))

    @override_settings(LLO_COP_RATE=1000)
    def test_commission_rate_llo_small_amount(self):
        # 50 LLO * 1000 = 50,000 COP -> 0.5% rate
        rate = Transfer.calculate_commission_rate(Decimal('50'), 'LLO')
        self.assertEqual(rate, Decimal('0.0050'))

    def test_commission_amount_calculation(self):
        transfer = Transfer(
            amount=Decimal('200000'),
            currency='COP',
        )
        commission = transfer.calculate_commission()
        self.assertEqual(commission, Decimal('2000.00'))
        self.assertEqual(transfer.commission_rate, Decimal('0.0100'))
        self.assertEqual(transfer.commission_amount, Decimal('2000.00'))


class TransferLimitTest(TransferModelTestMixin, TestCase):
    """Tests para la verificacion de limites de transferencia."""

    def setUp(self):
        self.user = self.create_user('+573001111111')
        self.limit = self.user.transfer_limit

    def test_per_transaction_within_limit(self):
        ok, msg = self.limit.check_per_transaction(Decimal('1000000'))
        self.assertTrue(ok)
        self.assertEqual(msg, '')

    def test_per_transaction_exceeds_limit(self):
        ok, msg = self.limit.check_per_transaction(Decimal('3000000'))
        self.assertFalse(ok)
        self.assertIn('limite por transaccion', msg)

    def test_daily_limit_within(self):
        ok, msg = self.limit.check_daily_limit(Decimal('1000000'))
        self.assertTrue(ok)

    def test_daily_limit_exceeds_after_transfers(self):
        # Simular transferencia completada hoy
        receiver = self.create_user('+573002222222')
        Transfer.objects.create(
            sender=self.user,
            receiver=receiver,
            amount=Decimal('4500000'),
            currency='COP',
            status=Transfer.Status.COMPLETED,
        )
        ok, msg = self.limit.check_daily_limit(Decimal('600000'))
        self.assertFalse(ok)
        self.assertIn('limite diario', msg)

    def test_monthly_limit_within(self):
        ok, msg = self.limit.check_monthly_limit(Decimal('5000000'))
        self.assertTrue(ok)

    def test_monthly_limit_exceeds(self):
        receiver = self.create_user('+573003333333')
        Transfer.objects.create(
            sender=self.user,
            receiver=receiver,
            amount=Decimal('19000000'),
            currency='COP',
            status=Transfer.Status.COMPLETED,
        )
        ok, msg = self.limit.check_monthly_limit(Decimal('2000000'))
        self.assertFalse(ok)
        self.assertIn('limite mensual', msg)

    def test_check_all_limits_first_failure(self):
        # Per-transaction limit should fail first
        ok, msg = self.limit.check_all_limits(Decimal('3000000'))
        self.assertFalse(ok)
        self.assertIn('limite por transaccion', msg)

    @override_settings(LLO_COP_RATE=1000)
    def test_limit_check_converts_llo_to_cop(self):
        # 3000 LLO * 1000 = 3,000,000 COP > 2M per-transaction limit
        ok, msg = self.limit.check_per_transaction(Decimal('3000'), currency='LLO')
        self.assertFalse(ok)


class TransferExecutionTest(TransferModelTestMixin, TestCase):
    """Tests para la ejecucion atomica de transferencias."""

    def setUp(self):
        self.sender = self.create_user('+573001111111', balance_cop=Decimal('500000'))
        self.receiver = self.create_user('+573002222222', balance_cop=Decimal('100000'))
        MasterWallet.objects.get_master()

    def test_successful_cop_transfer(self):
        transfer = Transfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('50000'),
            currency='COP',
            status=Transfer.Status.PENDING,
        )
        transfer.execute()

        transfer.refresh_from_db()
        self.assertEqual(transfer.status, Transfer.Status.COMPLETED)
        self.assertIsNotNone(transfer.completed_at)
        self.assertEqual(transfer.commission_rate, Decimal('0.0050'))
        self.assertEqual(transfer.commission_amount, Decimal('250.00'))

        # Verificar saldos
        self.sender.wallet.refresh_from_db()
        self.receiver.wallet.refresh_from_db()
        # Sender: 500,000 - 50,000 - 250 (commission) = 449,750
        self.assertEqual(self.sender.wallet.balance_cop, Decimal('449750.00'))
        # Receiver: 100,000 + 50,000 = 150,000
        self.assertEqual(self.receiver.wallet.balance_cop, Decimal('150000.00'))

    def test_transaction_records_created(self):
        transfer = Transfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('50000'),
            currency='COP',
            status=Transfer.Status.PENDING,
        )
        transfer.execute()

        # Transaccion de salida (TRANSFER_OUT) para remitente
        sender_txn = Transaction.objects.filter(
            wallet=self.sender.wallet,
            transaction_type=Transaction.TransactionType.TRANSFER_OUT,
        ).first()
        self.assertIsNotNone(sender_txn)
        self.assertEqual(sender_txn.amount, Decimal('50000'))
        self.assertEqual(sender_txn.status, Transaction.Status.COMPLETED)

        # Transaccion de entrada (TRANSFER_IN) para destinatario
        receiver_txn = Transaction.objects.filter(
            wallet=self.receiver.wallet,
            transaction_type=Transaction.TransactionType.TRANSFER_IN,
        ).first()
        self.assertIsNotNone(receiver_txn)
        self.assertEqual(receiver_txn.amount, Decimal('50000'))

        # Transaccion de comision para remitente
        commission_txn = Transaction.objects.filter(
            wallet=self.sender.wallet,
            transaction_type=Transaction.TransactionType.COMMISSION,
        ).first()
        self.assertIsNotNone(commission_txn)
        self.assertEqual(commission_txn.amount, Decimal('250.00'))

    def test_master_wallet_receives_commission(self):
        transfer = Transfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('50000'),
            currency='COP',
            status=Transfer.Status.PENDING,
        )
        transfer.execute()

        master = MasterWallet.objects.get_master()
        self.assertEqual(master.balance_cop, Decimal('250.00'))

    def test_insufficient_balance_fails(self):
        transfer = Transfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('600000'),  # Mas del saldo de 500,000
            currency='COP',
            status=Transfer.Status.PENDING,
        )
        with self.assertRaises(ValidationError):
            transfer.execute()

        transfer.refresh_from_db()
        self.assertEqual(transfer.status, Transfer.Status.FAILED)

    def test_cannot_execute_completed_transfer(self):
        transfer = Transfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('10000'),
            currency='COP',
            status=Transfer.Status.COMPLETED,
            completed_at=timezone.now(),
        )
        with self.assertRaises(ValidationError):
            transfer.execute()

    def test_inactive_sender_wallet_fails(self):
        self.sender.wallet.is_active = False
        self.sender.wallet.save()

        transfer = Transfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('10000'),
            currency='COP',
            status=Transfer.Status.PENDING,
        )
        with self.assertRaises(ValidationError):
            transfer.execute()

        transfer.refresh_from_db()
        self.assertEqual(transfer.status, Transfer.Status.FAILED)

    @override_settings(LLO_COP_RATE=1000)
    def test_successful_llo_transfer(self):
        transfer = Transfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('100'),
            currency='LLO',
            status=Transfer.Status.PENDING,
        )
        transfer.execute()

        transfer.refresh_from_db()
        self.assertEqual(transfer.status, Transfer.Status.COMPLETED)

        # 100 LLO * 1000 = 100,000 COP -> 1% rate -> 1 LLO commission
        self.assertEqual(transfer.commission_rate, Decimal('0.0100'))
        self.assertEqual(transfer.commission_amount, Decimal('1.00'))

        self.sender.wallet.refresh_from_db()
        self.receiver.wallet.refresh_from_db()
        # Sender: 500 - 100 - 1 = 399
        self.assertEqual(self.sender.wallet.balance_llo, Decimal('399.00'))
        # Receiver: 500 + 100 = 600
        self.assertEqual(self.receiver.wallet.balance_llo, Decimal('600.00'))

    def test_otp_required_transfer_can_execute(self):
        transfer = Transfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('50000'),
            currency='COP',
            status=Transfer.Status.OTP_REQUIRED,
        )
        transfer.otp_verified = True
        transfer.save()
        transfer.execute()

        transfer.refresh_from_db()
        self.assertEqual(transfer.status, Transfer.Status.COMPLETED)


class TransferCreationTest(TransferModelTestMixin, TestCase):
    """Tests para la creacion de transferencias a traves del serializer."""

    def setUp(self):
        self.sender = self.create_user('+573001111111', balance_cop=Decimal('2000000'))
        self.receiver = self.create_user('+573002222222', balance_cop=Decimal('100000'))

    def test_transfer_reference_is_unique(self):
        t1 = Transfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('10000'),
            currency='COP',
        )
        t2 = Transfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('20000'),
            currency='COP',
        )
        self.assertNotEqual(t1.reference, t2.reference)

    def test_transfer_default_status(self):
        transfer = Transfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('10000'),
            currency='COP',
        )
        self.assertEqual(transfer.status, Transfer.Status.PENDING)
        self.assertFalse(transfer.otp_verified)

    def test_scheduled_transfer_creation(self):
        scheduled = ScheduledTransfer.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('100000'),
            currency='COP',
            frequency=ScheduledTransfer.Frequency.MONTHLY,
            next_execution_date=timezone.now().date(),
            description='Pago mensual',
        )
        self.assertTrue(scheduled.is_active)
        self.assertEqual(scheduled.frequency, 'MONTHLY')
