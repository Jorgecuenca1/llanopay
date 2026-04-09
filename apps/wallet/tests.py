from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase, TransactionTestCase

from apps.wallet.models import Wallet, Transaction, MasterWallet

User = get_user_model()


class WalletModelTests(TestCase):
    """Tests para operaciones basicas de la billetera."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@llanopay.co',
            password='testpass123',
        )
        self.wallet = Wallet.objects.get_or_create(user=self.user)[0]

    def test_wallet_created_with_zero_balances(self):
        self.assertEqual(self.wallet.balance_cop, Decimal('0'))
        self.assertEqual(self.wallet.balance_llo, Decimal('0'))
        self.assertTrue(self.wallet.is_active)

    def test_deposit_cop(self):
        result = self.wallet.deposit_cop(Decimal('50000.00'))
        self.assertEqual(result, Decimal('50000.00'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance_cop, Decimal('50000.00'))

    def test_withdraw_cop(self):
        self.wallet.deposit_cop(Decimal('100000.00'))
        result = self.wallet.withdraw_cop(Decimal('30000.00'))
        self.assertEqual(result, Decimal('70000.00'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance_cop, Decimal('70000.00'))

    def test_withdraw_cop_insufficient_balance(self):
        self.wallet.deposit_cop(Decimal('10000.00'))
        with self.assertRaises(ValidationError):
            self.wallet.withdraw_cop(Decimal('50000.00'))

    def test_deposit_cop_negative_amount(self):
        with self.assertRaises(ValidationError):
            self.wallet.deposit_cop(Decimal('-100.00'))

    def test_withdraw_cop_negative_amount(self):
        with self.assertRaises(ValidationError):
            self.wallet.withdraw_cop(Decimal('-100.00'))

    def test_deposit_llo(self):
        result = self.wallet.deposit_llo(Decimal('25.50'))
        self.assertEqual(result, Decimal('25.50'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance_llo, Decimal('25.50'))

    def test_withdraw_llo(self):
        self.wallet.deposit_llo(Decimal('100.00'))
        result = self.wallet.withdraw_llo(Decimal('40.00'))
        self.assertEqual(result, Decimal('60.00'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance_llo, Decimal('60.00'))

    def test_withdraw_llo_insufficient_balance(self):
        self.wallet.deposit_llo(Decimal('10.00'))
        with self.assertRaises(ValidationError):
            self.wallet.withdraw_llo(Decimal('50.00'))

    def test_deposit_llo_negative_amount(self):
        with self.assertRaises(ValidationError):
            self.wallet.deposit_llo(Decimal('-5.00'))

    def test_multiple_deposits_cop(self):
        self.wallet.deposit_cop(Decimal('10000.00'))
        self.wallet.deposit_cop(Decimal('20000.00'))
        self.wallet.deposit_cop(Decimal('5000.00'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance_cop, Decimal('35000.00'))

    def test_wallet_str(self):
        self.assertIn('Billetera de', str(self.wallet))


class TransactionModelTests(TestCase):
    """Tests para el modelo de transacciones."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='txnuser',
            email='txn@llanopay.co',
            password='testpass123',
        )
        self.wallet = Wallet.objects.get_or_create(user=self.user)[0]

    def test_create_transaction(self):
        txn = Transaction.objects.create(
            wallet=self.wallet,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            amount=Decimal('50000.00'),
            currency=Transaction.Currency.COP,
            balance_after=Decimal('50000.00'),
            reference='DEP-001',
            description='Deposito de prueba',
            status=Transaction.Status.COMPLETED,
        )
        self.assertEqual(txn.transaction_type, 'DEPOSIT')
        self.assertEqual(txn.currency, 'COP')
        self.assertEqual(txn.status, 'COMPLETED')
        self.assertEqual(txn.amount, Decimal('50000.00'))

    def test_transaction_default_status_pending(self):
        txn = Transaction.objects.create(
            wallet=self.wallet,
            transaction_type=Transaction.TransactionType.WITHDRAWAL,
            amount=Decimal('10000.00'),
            currency=Transaction.Currency.COP,
            balance_after=Decimal('40000.00'),
        )
        self.assertEqual(txn.status, Transaction.Status.PENDING)

    def test_transaction_ordering(self):
        txn1 = Transaction.objects.create(
            wallet=self.wallet,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            amount=Decimal('10000.00'),
            currency=Transaction.Currency.COP,
            balance_after=Decimal('10000.00'),
        )
        txn2 = Transaction.objects.create(
            wallet=self.wallet,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            amount=Decimal('20000.00'),
            currency=Transaction.Currency.COP,
            balance_after=Decimal('30000.00'),
        )
        transactions = list(Transaction.objects.filter(wallet=self.wallet))
        self.assertEqual(transactions[0].pk, txn2.pk)

    def test_transaction_str(self):
        txn = Transaction.objects.create(
            wallet=self.wallet,
            transaction_type=Transaction.TransactionType.LLO_PURCHASE,
            amount=Decimal('5.00'),
            currency=Transaction.Currency.LLO,
            balance_after=Decimal('5.00'),
            status=Transaction.Status.COMPLETED,
        )
        self.assertIn('Compra de LLO', str(txn))

    def test_transaction_metadata_default(self):
        txn = Transaction.objects.create(
            wallet=self.wallet,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            amount=Decimal('1000.00'),
            currency=Transaction.Currency.COP,
            balance_after=Decimal('1000.00'),
        )
        self.assertEqual(txn.metadata, {})

    def test_transaction_with_metadata(self):
        txn = Transaction.objects.create(
            wallet=self.wallet,
            transaction_type=Transaction.TransactionType.CRYPTO_DEPOSIT,
            amount=Decimal('0.5'),
            currency=Transaction.Currency.LLO,
            balance_after=Decimal('0.5'),
            metadata={'tx_hash': '0xabc123', 'network': 'polygon'},
        )
        self.assertEqual(txn.metadata['tx_hash'], '0xabc123')


class MasterWalletTests(TestCase):
    """Tests para el patron singleton de la billetera maestra."""

    def test_master_wallet_singleton(self):
        master1 = MasterWallet.objects.get_master()
        master2 = MasterWallet.objects.get_master()
        self.assertEqual(master1.pk, master2.pk)
        self.assertEqual(master1.pk, 1)

    def test_master_wallet_defaults(self):
        master = MasterWallet.objects.get_master()
        self.assertEqual(master.balance_cop, Decimal('0'))
        self.assertEqual(master.balance_llo, Decimal('0'))
        self.assertEqual(master.total_crypto_reserves_usd, Decimal('0'))

    def test_master_wallet_save_forces_pk_1(self):
        master = MasterWallet(balance_cop=Decimal('1000000.00'))
        master.save()
        self.assertEqual(master.pk, 1)

    def test_master_wallet_str(self):
        master = MasterWallet.objects.get_master()
        self.assertIn('Billetera Maestra', str(master))


class WalletAtomicTests(TransactionTestCase):
    """Tests para operaciones atomicas concurrentes en la billetera.

    Usa TransactionTestCase para permitir que multiples hilos
    utilicen conexiones de base de datos independientes.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='atomicuser',
            email='atomic@llanopay.co',
            password='testpass123',
        )
        self.wallet = Wallet.objects.get_or_create(user=self.user)[0]
        self.wallet.deposit_cop(Decimal('1000000.00'))

    def test_concurrent_deposits_cop(self):
        """Multiples depositos concurrentes deben producir el saldo correcto."""
        num_deposits = 10
        amount_each = Decimal('1000.00')

        def do_deposit():
            from django import db
            db.connections.close_all()
            w = Wallet.objects.get(pk=self.wallet.pk)
            w.deposit_cop(amount_each)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(do_deposit) for _ in range(num_deposits)]
            for future in as_completed(futures):
                future.result()

        self.wallet.refresh_from_db()
        expected = Decimal('1000000.00') + (amount_each * num_deposits)
        self.assertEqual(self.wallet.balance_cop, expected)

    def test_concurrent_withdrawals_cop(self):
        """Retiros concurrentes no deben dejar saldo negativo."""
        num_withdrawals = 5
        amount_each = Decimal('200000.00')

        def do_withdrawal():
            from django import db
            db.connections.close_all()
            w = Wallet.objects.get(pk=self.wallet.pk)
            w.withdraw_cop(amount_each)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(do_withdrawal) for _ in range(num_withdrawals)]
            for future in as_completed(futures):
                future.result()

        self.wallet.refresh_from_db()
        expected = Decimal('1000000.00') - (amount_each * num_withdrawals)
        self.assertEqual(self.wallet.balance_cop, expected)
        self.assertGreaterEqual(self.wallet.balance_cop, Decimal('0'))


class WalletSignalTests(TestCase):
    """Tests para la creacion automatica de billetera por signal."""

    def test_wallet_auto_created_on_user_creation(self):
        user = User.objects.create_user(
            username='signaluser',
            email='signal@llanopay.co',
            password='testpass123',
        )
        self.assertTrue(Wallet.objects.filter(user=user).exists())

    def test_wallet_not_duplicated_on_user_save(self):
        user = User.objects.create_user(
            username='saveuser',
            email='save@llanopay.co',
            password='testpass123',
        )
        user.save()  # second save should not duplicate
        self.assertEqual(Wallet.objects.filter(user=user).count(), 1)
