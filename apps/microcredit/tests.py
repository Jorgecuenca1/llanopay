from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import User
from apps.microcredit.models import (
    CreditProfile,
    Microcredit,
    MicrocreditPayment,
    MicrocreditProduct,
)


class CreditProfileModelTest(TestCase):
    """Tests para el modelo CreditProfile y calculo de score."""

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='+573001234567',
            password='testpass123!',
            document_type='CC',
            document_number='1234567890',
            first_name='Juan',
            last_name='Perez',
        )
        self.profile = CreditProfile.objects.create(user=self.user)
        self.product = MicrocreditProduct.objects.create(
            name='Credito Campesino',
            description='Microcredito para campesinos del Llano.',
            min_amount=Decimal('50000'),
            max_amount=Decimal('2000000'),
            interest_rate_monthly=Decimal('2.0'),
            term_days=90,
            grace_period_days=5,
        )

    def test_initial_score_is_zero(self):
        """El puntaje inicial debe ser 0."""
        self.assertEqual(self.profile.credit_score, 0)

    def test_calculate_score_new_user(self):
        """Un usuario nuevo debe obtener un puntaje base."""
        score = self.profile.calculate_score()
        # Usuario nuevo: 100 (sin pagos) + 0 (sin prestamos) + 0 (sin pagos)
        # + 0 (cuenta nueva) + 100 (sin prestamos activos) = 200
        self.assertGreaterEqual(score, 100)
        self.assertLessEqual(score, 1000)
        self.assertIsNotNone(self.profile.last_evaluated_at)

    def test_calculate_score_with_good_payments(self):
        """Un usuario con buenos pagos debe tener puntaje alto."""
        self.profile.on_time_payments = 10
        self.profile.late_payments = 0
        self.profile.total_repaid = Decimal('1500000')
        self.profile.save()

        # Crear un prestamo pagado
        Microcredit.objects.create(
            user=self.user,
            product=self.product,
            amount_requested=Decimal('500000'),
            amount_approved=Decimal('500000'),
            interest_rate=Decimal('2.0'),
            term_days=90,
            total_to_repay=Decimal('530000'),
            amount_repaid=Decimal('530000'),
            status=Microcredit.Status.PAID,
            paid_at=timezone.now(),
        )

        score = self.profile.calculate_score()
        self.assertGreater(score, 400)

    def test_calculate_score_with_late_payments(self):
        """Pagos tardios reducen el puntaje."""
        self.profile.on_time_payments = 2
        self.profile.late_payments = 8
        self.profile.save()

        score = self.profile.calculate_score()
        # Ratio bajo de pagos a tiempo = puntaje menor
        self.assertLess(score, 500)

    def test_calculate_score_with_defaults(self):
        """Prestamos en mora penalizan fuertemente."""
        Microcredit.objects.create(
            user=self.user,
            product=self.product,
            amount_requested=Decimal('500000'),
            interest_rate=Decimal('2.0'),
            term_days=90,
            total_to_repay=Decimal('530000'),
            status=Microcredit.Status.DEFAULTED,
        )

        score = self.profile.calculate_score()
        self.assertLess(score, 200)

    def test_max_credit_amount_based_on_score(self):
        """El monto maximo de credito se calcula segun el puntaje."""
        self.profile.on_time_payments = 20
        self.profile.late_payments = 0
        self.profile.total_repaid = Decimal('6000000')
        self.profile.save()

        # Crear varios prestamos pagados
        for i in range(5):
            Microcredit.objects.create(
                user=self.user,
                product=self.product,
                amount_requested=Decimal('1000000'),
                amount_approved=Decimal('1000000'),
                interest_rate=Decimal('2.0'),
                term_days=90,
                total_to_repay=Decimal('1060000'),
                amount_repaid=Decimal('1060000'),
                status=Microcredit.Status.PAID,
                paid_at=timezone.now(),
            )

        self.profile.calculate_score()
        self.assertGreater(self.profile.max_credit_amount, Decimal('0'))

    def test_score_never_negative(self):
        """El puntaje nunca debe ser negativo."""
        # Crear multiples prestamos en mora
        for i in range(5):
            Microcredit.objects.create(
                user=self.user,
                product=self.product,
                amount_requested=Decimal('500000'),
                interest_rate=Decimal('2.0'),
                term_days=90,
                total_to_repay=Decimal('530000'),
                status=Microcredit.Status.DEFAULTED,
            )

        score = self.profile.calculate_score()
        self.assertGreaterEqual(score, 0)

    def test_score_never_exceeds_1000(self):
        """El puntaje nunca debe exceder 1000."""
        self.profile.on_time_payments = 1000
        self.profile.late_payments = 0
        self.profile.total_repaid = Decimal('100000000')
        self.profile.save()

        score = self.profile.calculate_score()
        self.assertLessEqual(score, 1000)


class MicrocreditProductModelTest(TestCase):
    """Tests para el modelo MicrocreditProduct."""

    def test_create_credito_campesino(self):
        """Crear producto Credito Campesino."""
        product = MicrocreditProduct.objects.create(
            name='Credito Campesino',
            description='Microcredito para campesinos del Llano.',
            min_amount=Decimal('50000'),
            max_amount=Decimal('2000000'),
            interest_rate_monthly=Decimal('1.5'),
            term_days=120,
            grace_period_days=15,
            requires_llo_collateral=False,
        )
        self.assertEqual(str(product), 'Credito Campesino (1.5% mensual)')
        self.assertTrue(product.is_active)

    def test_create_credito_comerciante(self):
        """Crear producto Credito Comerciante."""
        product = MicrocreditProduct.objects.create(
            name='Credito Comerciante',
            description='Microcredito para comerciantes del Llano.',
            min_amount=Decimal('100000'),
            max_amount=Decimal('5000000'),
            interest_rate_monthly=Decimal('2.5'),
            term_days=180,
            grace_period_days=0,
            requires_llo_collateral=True,
            llo_collateral_percentage=Decimal('10'),
        )
        self.assertTrue(product.requires_llo_collateral)
        self.assertEqual(product.llo_collateral_percentage, Decimal('10'))

    def test_clean_min_greater_than_max(self):
        """Validar que min_amount no sea mayor a max_amount."""
        product = MicrocreditProduct(
            name='Producto invalido',
            min_amount=Decimal('5000000'),
            max_amount=Decimal('100000'),
            interest_rate_monthly=Decimal('2.0'),
            term_days=90,
        )
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            product.clean()


class MicrocreditModelTest(TestCase):
    """Tests para el modelo Microcredit."""

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='+573009876543',
            password='testpass123!',
            document_type='CC',
            document_number='9876543210',
            first_name='Maria',
            last_name='Lopez',
        )
        self.product = MicrocreditProduct.objects.create(
            name='Credito Campesino',
            min_amount=Decimal('50000'),
            max_amount=Decimal('2000000'),
            interest_rate_monthly=Decimal('2.0'),
            term_days=90,
        )

    def test_calculate_total_to_repay(self):
        """Calcular total a pagar con intereses."""
        microcredit = Microcredit(
            user=self.user,
            product=self.product,
            amount_requested=Decimal('1000000'),
            amount_approved=Decimal('1000000'),
            interest_rate=Decimal('2.0'),
            term_days=90,
            total_to_repay=Decimal('0'),
        )
        total = microcredit.calculate_total_to_repay()
        # 1,000,000 * 2% * 3 meses = 60,000 de intereses
        # Total = 1,060,000
        self.assertEqual(total, Decimal('1060000.00'))

    def test_remaining_balance(self):
        """Verificar saldo pendiente."""
        microcredit = Microcredit.objects.create(
            user=self.user,
            product=self.product,
            amount_requested=Decimal('500000'),
            amount_approved=Decimal('500000'),
            interest_rate=Decimal('2.0'),
            term_days=90,
            total_to_repay=Decimal('530000'),
            amount_repaid=Decimal('200000'),
            status=Microcredit.Status.ACTIVE,
        )
        self.assertEqual(microcredit.remaining_balance, Decimal('330000'))

    def test_is_overdue(self):
        """Verificar deteccion de credito vencido."""
        microcredit = Microcredit.objects.create(
            user=self.user,
            product=self.product,
            amount_requested=Decimal('500000'),
            interest_rate=Decimal('2.0'),
            term_days=90,
            total_to_repay=Decimal('530000'),
            status=Microcredit.Status.ACTIVE,
            due_date=timezone.now() - timezone.timedelta(days=10),
        )
        self.assertTrue(microcredit.is_overdue)

    def test_is_not_overdue(self):
        """Credito con fecha futura no esta vencido."""
        microcredit = Microcredit.objects.create(
            user=self.user,
            product=self.product,
            amount_requested=Decimal('500000'),
            interest_rate=Decimal('2.0'),
            term_days=90,
            total_to_repay=Decimal('530000'),
            status=Microcredit.Status.ACTIVE,
            due_date=timezone.now() + timezone.timedelta(days=30),
        )
        self.assertFalse(microcredit.is_overdue)


class MicrocreditRequestAPITest(APITestCase):
    """Tests para la API de solicitud de microcredito."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number='+573005551234',
            password='testpass123!',
            document_type='CC',
            document_number='5551234567',
            first_name='Carlos',
            last_name='Ramirez',
        )
        self.client.force_authenticate(user=self.user)

        self.product = MicrocreditProduct.objects.create(
            name='Credito Campesino',
            description='Microcredito para campesinos.',
            min_amount=Decimal('50000'),
            max_amount=Decimal('2000000'),
            interest_rate_monthly=Decimal('2.0'),
            term_days=90,
            grace_period_days=5,
        )

        # Crear perfil crediticio con limite suficiente
        self.profile = CreditProfile.objects.create(
            user=self.user,
            credit_score=500,
            max_credit_amount=Decimal('1500000'),
        )

    def test_request_microcredit_success(self):
        """Solicitar un microcredito exitosamente."""
        response = self.client.post('/api/v1/microcredit/request/', {
            'product_id': str(self.product.pk),
            'amount_requested': '500000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount_requested'], '500000.00')
        self.assertEqual(response.data['status'], 'REQUESTED')

    def test_request_below_minimum(self):
        """Rechazar solicitud por debajo del monto minimo."""
        response = self.client.post('/api/v1/microcredit/request/', {
            'product_id': str(self.product.pk),
            'amount_requested': '10000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_above_maximum(self):
        """Rechazar solicitud por encima del monto maximo del producto."""
        response = self.client.post('/api/v1/microcredit/request/', {
            'product_id': str(self.product.pk),
            'amount_requested': '5000000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_above_credit_limit(self):
        """Rechazar solicitud por encima del limite crediticio."""
        response = self.client.post('/api/v1/microcredit/request/', {
            'product_id': str(self.product.pk),
            'amount_requested': '1600000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_inactive_product(self):
        """Rechazar solicitud para producto inactivo."""
        self.product.is_active = False
        self.product.save()

        response = self.client.post('/api/v1/microcredit/request/', {
            'product_id': str(self.product.pk),
            'amount_requested': '500000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_max_active_loans(self):
        """Rechazar solicitud si ya tiene 3 prestamos activos."""
        for i in range(3):
            Microcredit.objects.create(
                user=self.user,
                product=self.product,
                amount_requested=Decimal('100000'),
                interest_rate=Decimal('2.0'),
                term_days=90,
                total_to_repay=Decimal('106000'),
                status=Microcredit.Status.ACTIVE,
            )

        response = self.client.post('/api/v1/microcredit/request/', {
            'product_id': str(self.product.pk),
            'amount_requested': '100000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_request(self):
        """Rechazar solicitud sin autenticacion."""
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/v1/microcredit/request/', {
            'product_id': str(self.product.pk),
            'amount_requested': '500000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MicrocreditPaymentAPITest(APITestCase):
    """Tests para la API de pagos de microcredito."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number='+573007771234',
            password='testpass123!',
            document_type='CC',
            document_number='7771234567',
            first_name='Ana',
            last_name='Gutierrez',
        )
        self.client.force_authenticate(user=self.user)

        self.product = MicrocreditProduct.objects.create(
            name='Credito Comerciante',
            min_amount=Decimal('100000'),
            max_amount=Decimal('5000000'),
            interest_rate_monthly=Decimal('2.5'),
            term_days=180,
        )

        self.profile = CreditProfile.objects.create(
            user=self.user,
            credit_score=600,
            max_credit_amount=Decimal('3000000'),
        )

        self.microcredit = Microcredit.objects.create(
            user=self.user,
            product=self.product,
            amount_requested=Decimal('1000000'),
            amount_approved=Decimal('1000000'),
            interest_rate=Decimal('2.5'),
            term_days=180,
            total_to_repay=Decimal('1150000'),
            amount_repaid=Decimal('0'),
            status=Microcredit.Status.ACTIVE,
            disbursed_at=timezone.now(),
            due_date=timezone.now() + timezone.timedelta(days=180),
        )

    def test_make_partial_payment(self):
        """Realizar un pago parcial exitosamente."""
        response = self.client.post('/api/v1/microcredit/pay/', {
            'microcredit_id': str(self.microcredit.pk),
            'amount': '200000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount_paid'], '200000.00')
        self.assertEqual(response.data['remaining_balance'], '950000.00')

    def test_make_full_payment(self):
        """Pagar el total restante del credito."""
        response = self.client.post('/api/v1/microcredit/pay/', {
            'microcredit_id': str(self.microcredit.pk),
            'amount': '1150000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['remaining_balance'], '0.00')
        self.assertEqual(response.data['microcredit_status'], 'Pagado')

        # Verificar que el microcredito se marco como pagado
        self.microcredit.refresh_from_db()
        self.assertEqual(self.microcredit.status, Microcredit.Status.PAID)
        self.assertIsNotNone(self.microcredit.paid_at)

    def test_payment_exceeds_balance(self):
        """Rechazar pago que excede el saldo pendiente."""
        response = self.client.post('/api/v1/microcredit/pay/', {
            'microcredit_id': str(self.microcredit.pk),
            'amount': '2000000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_on_paid_loan(self):
        """Rechazar pago en un credito ya pagado."""
        self.microcredit.status = Microcredit.Status.PAID
        self.microcredit.save()

        response = self.client.post('/api/v1/microcredit/pay/', {
            'microcredit_id': str(self.microcredit.pk),
            'amount': '100000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_updates_credit_profile(self):
        """Verificar que el pago actualiza el perfil crediticio."""
        self.client.post('/api/v1/microcredit/pay/', {
            'microcredit_id': str(self.microcredit.pk),
            'amount': '200000.00',
        })

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_repaid, Decimal('200000.00'))
        self.assertEqual(self.profile.on_time_payments, 1)

    def test_payment_other_user_loan(self):
        """Rechazar pago en un credito de otro usuario."""
        other_user = User.objects.create_user(
            phone_number='+573008881234',
            password='testpass123!',
            document_type='CC',
            document_number='8881234567',
            first_name='Pedro',
            last_name='Diaz',
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.post('/api/v1/microcredit/pay/', {
            'microcredit_id': str(self.microcredit.pk),
            'amount': '100000.00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_multiple_payments_until_paid(self):
        """Realizar multiples pagos hasta completar el credito."""
        # Primer pago
        self.client.post('/api/v1/microcredit/pay/', {
            'microcredit_id': str(self.microcredit.pk),
            'amount': '500000.00',
        })

        # Segundo pago
        self.client.post('/api/v1/microcredit/pay/', {
            'microcredit_id': str(self.microcredit.pk),
            'amount': '500000.00',
        })

        # Tercer pago (resta 150,000)
        response = self.client.post('/api/v1/microcredit/pay/', {
            'microcredit_id': str(self.microcredit.pk),
            'amount': '150000.00',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['remaining_balance'], '0.00')

        self.microcredit.refresh_from_db()
        self.assertEqual(self.microcredit.status, Microcredit.Status.PAID)
        self.assertEqual(self.microcredit.amount_repaid, Decimal('1150000'))

        # Verificar pagos registrados
        payments = MicrocreditPayment.objects.filter(microcredit=self.microcredit)
        self.assertEqual(payments.count(), 3)


class CreditScoreRecalculateAPITest(APITestCase):
    """Tests para la API de recalculo de puntaje crediticio."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number='+573006661234',
            password='testpass123!',
            document_type='CC',
            document_number='6661234567',
            first_name='Luis',
            last_name='Martinez',
        )
        self.client.force_authenticate(user=self.user)

    def test_recalculate_score(self):
        """Recalcular puntaje crediticio exitosamente."""
        response = self.client.post('/api/v1/microcredit/score/recalculate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('credit_score', response.data)
        self.assertIn('max_credit_amount', response.data)

    def test_recalculate_creates_profile(self):
        """El recalculo crea el perfil si no existe."""
        self.assertFalse(CreditProfile.objects.filter(user=self.user).exists())

        response = self.client.post('/api/v1/microcredit/score/recalculate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CreditProfile.objects.filter(user=self.user).exists())


class MicrocreditListAPITest(APITestCase):
    """Tests para la API de listado de microcreditos."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number='+573004441234',
            password='testpass123!',
            document_type='CC',
            document_number='4441234567',
            first_name='Sofia',
            last_name='Torres',
        )
        self.client.force_authenticate(user=self.user)

        self.product = MicrocreditProduct.objects.create(
            name='Credito Campesino',
            min_amount=Decimal('50000'),
            max_amount=Decimal('2000000'),
            interest_rate_monthly=Decimal('2.0'),
            term_days=90,
        )

    def test_list_user_microcredits(self):
        """Listar microcreditos del usuario."""
        Microcredit.objects.create(
            user=self.user,
            product=self.product,
            amount_requested=Decimal('500000'),
            interest_rate=Decimal('2.0'),
            term_days=90,
            total_to_repay=Decimal('530000'),
            status=Microcredit.Status.ACTIVE,
        )
        response = self.client.get('/api/v1/microcredit/loans/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_status(self):
        """Filtrar microcreditos por estado."""
        Microcredit.objects.create(
            user=self.user,
            product=self.product,
            amount_requested=Decimal('500000'),
            interest_rate=Decimal('2.0'),
            term_days=90,
            total_to_repay=Decimal('530000'),
            status=Microcredit.Status.ACTIVE,
        )
        Microcredit.objects.create(
            user=self.user,
            product=self.product,
            amount_requested=Decimal('300000'),
            interest_rate=Decimal('2.0'),
            term_days=90,
            total_to_repay=Decimal('318000'),
            status=Microcredit.Status.PAID,
        )

        response = self.client.get('/api/v1/microcredit/loans/?status=ACTIVE')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_no_other_user_loans_visible(self):
        """No se deben ver prestamos de otros usuarios."""
        other_user = User.objects.create_user(
            phone_number='+573003331234',
            password='testpass123!',
            document_type='CC',
            document_number='3331234567',
            first_name='Pedro',
            last_name='Gomez',
        )
        Microcredit.objects.create(
            user=other_user,
            product=self.product,
            amount_requested=Decimal('500000'),
            interest_rate=Decimal('2.0'),
            term_days=90,
            total_to_repay=Decimal('530000'),
            status=Microcredit.Status.ACTIVE,
        )

        response = self.client.get('/api/v1/microcredit/loans/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_product_list(self):
        """Listar productos de microcredito disponibles."""
        response = self.client.get('/api/v1/microcredit/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Credito Campesino')

    def test_credit_profile(self):
        """Obtener perfil crediticio del usuario."""
        CreditProfile.objects.create(
            user=self.user,
            credit_score=450,
            max_credit_amount=Decimal('1500000'),
        )
        response = self.client.get('/api/v1/microcredit/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['credit_score'], 450)
