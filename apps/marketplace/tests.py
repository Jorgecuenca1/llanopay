from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.wallet.models import Wallet

from .models import (
    Merchant,
    MerchantCategory,
    MerchantPayment,
    MerchantReview,
)

User = get_user_model()


class MarketplaceTestBase(TestCase):
    """Base test class with common setup for marketplace tests."""

    def setUp(self):
        self.client = APIClient()

        # Crear usuarios
        self.merchant_user = User.objects.create_user(
            phone_number='+573001000001',
            password='testpass123',
            first_name='Carlos',
            last_name='Comerciante',
            document_type='CC',
            document_number='1001001001',
        )
        self.payer_user = User.objects.create_user(
            phone_number='+573001000002',
            password='testpass123',
            first_name='Ana',
            last_name='Compradora',
            document_type='CC',
            document_number='1001001002',
        )
        self.reviewer_user = User.objects.create_user(
            phone_number='+573001000003',
            password='testpass123',
            first_name='Pedro',
            last_name='Revisor',
            document_type='CC',
            document_number='1001001003',
        )

        # Crear billeteras
        self.merchant_wallet = Wallet.objects.create(
            user=self.merchant_user,
            balance_cop=Decimal('0'),
            balance_llo=Decimal('0'),
        )
        self.payer_wallet = Wallet.objects.create(
            user=self.payer_user,
            balance_cop=Decimal('500000'),
            balance_llo=Decimal('1000'),
        )

        # Crear categoria
        self.category = MerchantCategory.objects.create(
            name='Restaurantes',
            slug='restaurantes',
            icon='mdi-food',
            description='Restaurantes y comida',
        )


class MerchantRegistrationTests(MarketplaceTestBase):
    """Tests para el registro de comerciantes."""

    def test_register_merchant_success(self):
        """Un usuario autenticado puede registrarse como comerciante."""
        self.client.force_authenticate(user=self.merchant_user)
        data = {
            'business_name': 'Asados del Llano',
            'category': self.category.pk,
            'description': 'Los mejores asados de la region llanera',
            'address': 'Calle 10 #5-20, Villavicencio',
            'city': 'Villavicencio',
            'department': 'META',
            'phone': '+573001234567',
            'whatsapp': '+573001234567',
            'latitude': '4.142000',
            'longitude': '-73.626700',
        }
        response = self.client.post(
            reverse('marketplace:merchant-register'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['business_name'], 'Asados del Llano')
        self.assertEqual(response.data['department'], 'META')
        # Verificar que el usuario se marco como comerciante
        self.merchant_user.refresh_from_db()
        self.assertTrue(self.merchant_user.is_merchant)

    def test_register_merchant_duplicate(self):
        """No se puede registrar dos veces como comerciante."""
        self.client.force_authenticate(user=self.merchant_user)
        Merchant.objects.create(
            user=self.merchant_user,
            business_name='Negocio Existente',
            slug='negocio-existente',
            category=self.category,
            address='Dir 1',
            city='Villavicencio',
            department='META',
            phone='+573001234567',
        )
        data = {
            'business_name': 'Otro Negocio',
            'category': self.category.pk,
            'address': 'Dir 2',
            'city': 'Villavicencio',
            'department': 'META',
            'phone': '+573009876543',
        }
        response = self.client.post(
            reverse('marketplace:merchant-register'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_merchant_unauthenticated(self):
        """Un usuario no autenticado no puede registrarse como comerciante."""
        data = {
            'business_name': 'Negocio Sin Auth',
            'category': self.category.pk,
            'address': 'Dir',
            'city': 'Yopal',
            'department': 'CASANARE',
            'phone': '+573001111111',
        }
        response = self.client.post(
            reverse('marketplace:merchant-register'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MerchantPaymentTests(MarketplaceTestBase):
    """Tests para el flujo de pagos a comerciantes."""

    def setUp(self):
        super().setUp()
        self.merchant = Merchant.objects.create(
            user=self.merchant_user,
            business_name='Tienda Llanera',
            slug='tienda-llanera',
            category=self.category,
            address='Calle 5 #3-10',
            city='Villavicencio',
            department='META',
            phone='+573001234567',
            commission_rate=Decimal('2.00'),
            is_active=True,
        )

    def test_payment_cop_success(self):
        """Pago exitoso en COP a un comerciante."""
        self.client.force_authenticate(user=self.payer_user)
        data = {
            'merchant': self.merchant.pk,
            'amount': '50000.00',
            'currency': 'COP',
            'description': 'Almuerzo tipico llanero',
        }
        response = self.client.post(
            reverse('marketplace:merchant-payment'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'COMPLETED')
        # Verificar comision: 2% de 50000 = 1000
        self.assertEqual(Decimal(response.data['commission_amount']), Decimal('1000.00'))
        # Verificar saldo del pagador: 500000 - 50000 = 450000
        self.payer_wallet.refresh_from_db()
        self.assertEqual(self.payer_wallet.balance_cop, Decimal('450000.00'))
        # Verificar saldo del comerciante: 0 + (50000 - 1000) = 49000
        self.merchant_wallet.refresh_from_db()
        self.assertEqual(self.merchant_wallet.balance_cop, Decimal('49000.00'))
        # Verificar incremento de ventas
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.total_sales, 1)

    def test_payment_llo_success(self):
        """Pago exitoso en LLO a un comerciante."""
        self.client.force_authenticate(user=self.payer_user)
        data = {
            'merchant': self.merchant.pk,
            'amount': '100.00',
            'currency': 'LLO',
            'description': 'Compra con LlanoCoins',
        }
        response = self.client.post(
            reverse('marketplace:merchant-payment'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.payer_wallet.refresh_from_db()
        self.assertEqual(self.payer_wallet.balance_llo, Decimal('900.00'))

    def test_payment_insufficient_balance(self):
        """No se puede pagar si el saldo es insuficiente."""
        self.client.force_authenticate(user=self.payer_user)
        data = {
            'merchant': self.merchant.pk,
            'amount': '9999999.00',
            'currency': 'COP',
        }
        response = self.client.post(
            reverse('marketplace:merchant-payment'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_inactive_merchant(self):
        """No se puede pagar a un comerciante inactivo."""
        self.merchant.is_active = False
        self.merchant.save()
        self.client.force_authenticate(user=self.payer_user)
        data = {
            'merchant': self.merchant.pk,
            'amount': '10000.00',
            'currency': 'COP',
        }
        response = self.client.post(
            reverse('marketplace:merchant-payment'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_unauthenticated(self):
        """Un usuario no autenticado no puede realizar pagos."""
        data = {
            'merchant': self.merchant.pk,
            'amount': '10000.00',
            'currency': 'COP',
        }
        response = self.client.post(
            reverse('marketplace:merchant-payment'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MerchantReviewTests(MarketplaceTestBase):
    """Tests para resenas de comerciantes."""

    def setUp(self):
        super().setUp()
        self.merchant = Merchant.objects.create(
            user=self.merchant_user,
            business_name='Finca Ganadera',
            slug='finca-ganadera',
            category=self.category,
            address='Vereda La Esperanza',
            city='Acacias',
            department='META',
            phone='+573007654321',
            is_active=True,
        )

    def test_create_review_success(self):
        """Un usuario puede dejar una resena en un comerciante."""
        self.client.force_authenticate(user=self.reviewer_user)
        data = {
            'merchant': self.merchant.pk,
            'rating': 5,
            'comment': 'Excelente servicio, muy recomendado!',
        }
        response = self.client.post(
            reverse('marketplace:merchant-reviews-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        # Verificar que se actualizo el rating del comerciante
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.total_reviews, 1)
        self.assertEqual(self.merchant.rating, Decimal('5.00'))

    def test_duplicate_review_not_allowed(self):
        """Un usuario no puede dejar dos resenas al mismo comerciante."""
        MerchantReview.objects.create(
            merchant=self.merchant,
            user=self.reviewer_user,
            rating=4,
            comment='Buen servicio',
        )
        self.client.force_authenticate(user=self.reviewer_user)
        data = {
            'merchant': self.merchant.pk,
            'rating': 3,
            'comment': 'Quiero cambiar mi resena',
        }
        response = self.client.post(
            reverse('marketplace:merchant-reviews-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_cannot_review_own_merchant(self):
        """El dueno no puede dejar resena en su propio negocio."""
        self.client.force_authenticate(user=self.merchant_user)
        data = {
            'merchant': self.merchant.pk,
            'rating': 5,
            'comment': 'Mi propio negocio es genial',
        }
        response = self.client.post(
            reverse('marketplace:merchant-reviews-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reviews_public(self):
        """Cualquier usuario puede ver las resenas (sin autenticacion)."""
        MerchantReview.objects.create(
            merchant=self.merchant,
            user=self.reviewer_user,
            rating=4,
            comment='Buen servicio',
        )
        response = self.client.get(
            reverse('marketplace:merchant-reviews-list'),
            {'merchant': self.merchant.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_rating_range(self):
        """La calificacion debe estar entre 1 y 5."""
        self.client.force_authenticate(user=self.reviewer_user)
        # Rating demasiado alto
        data = {
            'merchant': self.merchant.pk,
            'rating': 6,
            'comment': 'Rating invalido',
        }
        response = self.client.post(
            reverse('marketplace:merchant-reviews-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
