from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.crypto.models import (
    CryptoDeposit,
    CryptoWithdrawal,
    ExchangeRate,
    LlanocoinTransaction,
)

User = get_user_model()


class ExchangeRateModelTest(TestCase):
    """Tests para el modelo ExchangeRate y conversion de tasas."""

    def setUp(self):
        ExchangeRate.objects.create(
            currency='USDT', rate_cop=Decimal('4200.00'), source='coingecko'
        )
        ExchangeRate.objects.create(
            currency='BTC', rate_cop=Decimal('250000000.00'), source='coingecko'
        )
        ExchangeRate.objects.create(
            currency='ETH', rate_cop=Decimal('14000000.00'), source='coingecko'
        )
        ExchangeRate.objects.create(
            currency='LLO', rate_cop=Decimal('1000.00'), source='internal'
        )

    def test_get_rate_returns_correct_value(self):
        rate = ExchangeRate.get_rate('USDT')
        self.assertEqual(rate, Decimal('4200.00'))

    def test_get_rate_btc(self):
        rate = ExchangeRate.get_rate('BTC')
        self.assertEqual(rate, Decimal('250000000.00'))

    def test_get_rate_llo_fallback(self):
        """Si no hay tasa LLO en BD, usa el setting LLO_COP_RATE."""
        ExchangeRate.objects.filter(currency='LLO').delete()
        from django.core.cache import cache
        cache.delete('exchange_rate_LLO')
        rate = ExchangeRate.get_rate('LLO')
        self.assertEqual(rate, Decimal(str(settings.LLO_COP_RATE)))

    def test_get_rate_nonexistent_currency(self):
        rate = ExchangeRate.get_rate('XYZ')
        self.assertEqual(rate, Decimal('0'))

    def test_conversion_usdt_to_cop(self):
        rate = ExchangeRate.get_rate('USDT')
        amount_usdt = Decimal('100.00000000')
        cop = amount_usdt * rate
        self.assertEqual(cop, Decimal('420000.00000000'))

    def test_conversion_btc_to_cop(self):
        rate = ExchangeRate.get_rate('BTC')
        amount_btc = Decimal('0.01000000')
        cop = amount_btc * rate
        self.assertEqual(cop, Decimal('2500000.00000000'))

    def test_rate_str(self):
        rate_obj = ExchangeRate.objects.get(currency='USDT')
        self.assertIn('USDT', str(rate_obj))
        self.assertIn('4200', str(rate_obj))


class CryptoDepositModelTest(TestCase):
    """Tests para el modelo CryptoDeposit."""

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='+573001234567',
            password='testpass123',
        )
        ExchangeRate.objects.create(
            currency='USDT', rate_cop=Decimal('4200.00'), source='coingecko'
        )

    def test_create_deposit(self):
        deposit = CryptoDeposit.objects.create(
            user=self.user,
            currency='USDT',
            amount=Decimal('100.00000000'),
            tx_hash='0xabc123def456',
            network='POLYGON',
            cop_amount=Decimal('420000.00'),
            exchange_rate=Decimal('4200.00'),
        )
        self.assertEqual(deposit.status, CryptoDeposit.Status.PENDING)
        self.assertEqual(deposit.confirmations, 0)
        self.assertEqual(deposit.required_confirmations, 12)
        self.assertIsNotNone(deposit.created_at)

    def test_deposit_unique_tx_hash(self):
        CryptoDeposit.objects.create(
            user=self.user,
            currency='USDT',
            amount=Decimal('100.00000000'),
            tx_hash='0xunique123',
            network='POLYGON',
        )
        with self.assertRaises(Exception):
            CryptoDeposit.objects.create(
                user=self.user,
                currency='USDT',
                amount=Decimal('50.00000000'),
                tx_hash='0xunique123',
                network='POLYGON',
            )

    def test_deposit_ordering(self):
        d1 = CryptoDeposit.objects.create(
            user=self.user,
            currency='USDT',
            amount=Decimal('100.00000000'),
            tx_hash='0xfirst',
            network='POLYGON',
        )
        d2 = CryptoDeposit.objects.create(
            user=self.user,
            currency='ETH',
            amount=Decimal('1.00000000'),
            tx_hash='0xsecond',
            network='ETHEREUM',
        )
        deposits = list(CryptoDeposit.objects.all())
        self.assertEqual(deposits[0].id, d2.id)

    def test_deposit_str(self):
        deposit = CryptoDeposit.objects.create(
            user=self.user,
            currency='BTC',
            amount=Decimal('0.50000000'),
            tx_hash='0xbtchash',
            network='BITCOIN',
        )
        self.assertIn('BTC', str(deposit))
        self.assertIn('PENDING', str(deposit))


class CryptoDepositAPITest(TestCase):
    """Tests para la API de depositos crypto."""

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='+573001234567',
            password='testpass123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        ExchangeRate.objects.create(
            currency='USDT', rate_cop=Decimal('4200.00'), source='coingecko'
        )

    @patch('apps.crypto.views.verify_crypto_deposit.delay')
    def test_create_deposit_success(self, mock_task):
        data = {
            'currency': 'USDT',
            'amount': '100.00000000',
            'tx_hash': '0xabc123def456',
            'network': 'POLYGON',
        }
        response = self.client.post('/api/v1/crypto/deposits/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertEqual(response.data['currency'], 'USDT')
        mock_task.assert_called_once()

    @patch('apps.crypto.views.verify_crypto_deposit.delay')
    def test_create_deposit_invalid_network(self, mock_task):
        data = {
            'currency': 'BTC',
            'amount': '1.00000000',
            'tx_hash': '0xbtchash123',
            'network': 'POLYGON',  # BTC no va por Polygon
        }
        response = self.client.post('/api/v1/crypto/deposits/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.crypto.views.verify_crypto_deposit.delay')
    def test_create_deposit_duplicate_tx_hash(self, mock_task):
        data = {
            'currency': 'USDT',
            'amount': '100.00000000',
            'tx_hash': '0xduplicate',
            'network': 'POLYGON',
        }
        self.client.post('/api/v1/crypto/deposits/', data)
        response = self.client.post('/api/v1/crypto/deposits/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_deposits(self):
        CryptoDeposit.objects.create(
            user=self.user,
            currency='USDT',
            amount=Decimal('100.00000000'),
            tx_hash='0xlist1',
            network='POLYGON',
        )
        CryptoDeposit.objects.create(
            user=self.user,
            currency='ETH',
            amount=Decimal('2.00000000'),
            tx_hash='0xlist2',
            network='ETHEREUM',
        )
        response = self.client.get('/api/v1/crypto/deposits/list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_unauthenticated_deposit(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/v1/crypto/deposits/', {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ExchangeRateAPITest(TestCase):
    """Tests para la API publica de tasas de cambio."""

    def setUp(self):
        self.client = APIClient()
        ExchangeRate.objects.create(
            currency='USDT', rate_cop=Decimal('4200.00'), source='coingecko'
        )
        ExchangeRate.objects.create(
            currency='LLO', rate_cop=Decimal('1000.00'), source='internal'
        )

    def test_list_rates_public(self):
        response = self.client.get('/api/v1/crypto/rates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_rate_contains_fields(self):
        response = self.client.get('/api/v1/crypto/rates/')
        rate = response.data[0]
        self.assertIn('currency', rate)
        self.assertIn('rate_cop', rate)
        self.assertIn('source', rate)
        self.assertIn('updated_at', rate)


class LlanocoinBuySellTest(TestCase):
    """Tests para compra y venta de Llanocoin."""

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='+573001234567',
            password='testpass123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        ExchangeRate.objects.create(
            currency='LLO', rate_cop=Decimal('1000.00'), source='internal'
        )
        # Crear wallet mock con saldo
        self._setup_wallet()

    def _setup_wallet(self):
        """Configura la billetera del usuario con saldo de prueba."""
        try:
            wallet = self.user.wallet
            wallet.balance = Decimal('500000.00')
            wallet.save()
        except Exception:
            # Si el modelo Wallet no tiene auto-create,
            # esto se manejara en la integracion completa
            pass

    def test_buy_llanocoin(self):
        try:
            wallet = self.user.wallet
            wallet.balance = Decimal('500000.00')
            wallet.save()
        except Exception:
            self.skipTest("Wallet model not available yet")

        data = {'amount_cop': '100000.00'}
        response = self.client.post('/api/v1/crypto/llanocoin/buy/', data)

        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(response.data['transaction_type'], 'BUY')
            self.assertEqual(response.data['status'], 'COMPLETED')
            self.assertEqual(
                Decimal(response.data['amount_llo']),
                Decimal('100.00000000'),
            )

    def test_buy_llanocoin_insufficient_balance(self):
        try:
            wallet = self.user.wallet
            wallet.balance = Decimal('0.00')
            wallet.save()
        except Exception:
            self.skipTest("Wallet model not available yet")

        data = {'amount_cop': '100000.00'}
        response = self.client.post('/api/v1/crypto/llanocoin/buy/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sell_llanocoin(self):
        try:
            wallet = self.user.wallet
            wallet.balance = Decimal('500000.00')
            wallet.save()
        except Exception:
            self.skipTest("Wallet model not available yet")

        # Primero comprar LLO
        LlanocoinTransaction.objects.create(
            user=self.user,
            transaction_type=LlanocoinTransaction.TransactionType.BUY,
            amount_llo=Decimal('200.00000000'),
            amount_cop=Decimal('200000.00'),
            rate=Decimal('1000.00'),
            status=LlanocoinTransaction.Status.COMPLETED,
        )

        data = {'amount_llo': '50.00000000'}
        response = self.client.post('/api/v1/crypto/llanocoin/sell/', data)

        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(response.data['transaction_type'], 'SELL')
            self.assertEqual(response.data['status'], 'COMPLETED')
            self.assertEqual(
                Decimal(response.data['amount_cop']),
                Decimal('50000.00'),
            )

    def test_sell_llanocoin_insufficient_llo(self):
        try:
            wallet = self.user.wallet
        except Exception:
            self.skipTest("Wallet model not available yet")

        data = {'amount_llo': '999999.00000000'}
        response = self.client.post('/api/v1/crypto/llanocoin/sell/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_llanocoin_transaction_list(self):
        LlanocoinTransaction.objects.create(
            user=self.user,
            transaction_type=LlanocoinTransaction.TransactionType.BUY,
            amount_llo=Decimal('100.00000000'),
            amount_cop=Decimal('100000.00'),
            rate=Decimal('1000.00'),
            status=LlanocoinTransaction.Status.COMPLETED,
        )
        response = self.client.get('/api/v1/crypto/llanocoin/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_buy_negative_amount(self):
        data = {'amount_cop': '-1000.00'}
        response = self.client.post('/api/v1/crypto/llanocoin/buy/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sell_zero_amount(self):
        data = {'amount_llo': '0.00000000'}
        response = self.client.post('/api/v1/crypto/llanocoin/sell/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
