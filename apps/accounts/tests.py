from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import OTPCode, User


class UserRegistrationTests(TestCase):
    """Tests for user registration."""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('accounts:register')
        self.valid_payload = {
            'phone_number': '+573001234567',
            'document_type': 'CC',
            'document_number': '1234567890',
            'first_name': 'Juan',
            'last_name': 'Perez',
            'password': 'SecurePass123!',
        }

    def test_register_user_success(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('otp_code', response.data)
        self.assertEqual(response.data['phone_number'], '+573001234567')
        self.assertTrue(User.objects.filter(phone_number='+573001234567').exists())

    def test_register_duplicate_phone(self):
        """Test registration with an already registered phone number."""
        User.objects.create_user(
            phone_number='+573001234567',
            password='OtherPass123!',
            document_type='CC',
            document_number='0000000000',
            first_name='Existing',
            last_name='User',
        )
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        """Test registration with missing required fields."""
        payload = {'phone_number': '+573009999999'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_creates_otp(self):
        """Test that registration creates an OTP code."""
        self.client.post(self.register_url, self.valid_payload, format='json')
        user = User.objects.get(phone_number='+573001234567')
        self.assertTrue(
            OTPCode.objects.filter(user=user, purpose=OTPCode.Purpose.REGISTER).exists()
        )


class OTPVerificationTests(TestCase):
    """Tests for OTP verification."""

    def setUp(self):
        self.client = APIClient()
        self.verify_url = reverse('accounts:verify-otp')
        self.user = User.objects.create_user(
            phone_number='+573007654321',
            password='TestPass123!',
            document_type='CC',
            document_number='9876543210',
            first_name='Maria',
            last_name='Lopez',
        )
        self.otp = OTPCode.objects.create(
            user=self.user,
            purpose=OTPCode.Purpose.REGISTER,
        )

    def test_verify_otp_success(self):
        """Test successful OTP verification."""
        response = self.client.post(
            self.verify_url,
            {
                'phone_number': '+573007654321',
                'code': self.otp.code,
                'purpose': 'REGISTER',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # User should now be verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_verify_otp_invalid_code(self):
        """Test OTP verification with invalid code."""
        response = self.client.post(
            self.verify_url,
            {
                'phone_number': '+573007654321',
                'code': '000000',
                'purpose': 'REGISTER',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_otp_expired(self):
        """Test OTP verification with expired code."""
        self.otp.expires_at = timezone.now() - timezone.timedelta(minutes=10)
        self.otp.save(update_fields=['expires_at'])

        response = self.client.post(
            self.verify_url,
            {
                'phone_number': '+573007654321',
                'code': self.otp.code,
                'purpose': 'REGISTER',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_otp_already_used(self):
        """Test OTP verification with already used code."""
        self.otp.is_used = True
        self.otp.save(update_fields=['is_used'])

        response = self.client.post(
            self.verify_url,
            {
                'phone_number': '+573007654321',
                'code': self.otp.code,
                'purpose': 'REGISTER',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(TestCase):
    """Tests for user login."""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('accounts:login')
        self.user = User.objects.create_user(
            phone_number='+573005551234',
            password='LoginPass123!',
            document_type='CC',
            document_number='1112223334',
            first_name='Carlos',
            last_name='Garcia',
            is_verified=True,
        )

    def test_login_success(self):
        """Test successful login with valid credentials."""
        response = self.client.post(
            self.login_url,
            {
                'phone_number': '+573005551234',
                'password': 'LoginPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_wrong_password(self):
        """Test login with wrong password."""
        response = self.client.post(
            self.login_url,
            {
                'phone_number': '+573005551234',
                'password': 'WrongPassword123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Test login with non-existent phone number."""
        response = self.client.post(
            self.login_url,
            {
                'phone_number': '+573000000000',
                'password': 'SomePass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unverified_user(self):
        """Test login with unverified user."""
        self.user.is_verified = False
        self.user.save(update_fields=['is_verified'])

        response = self.client.post(
            self.login_url,
            {
                'phone_number': '+573005551234',
                'password': 'LoginPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileUpdateTests(TestCase):
    """Tests for user profile update."""

    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse('accounts:profile')
        self.user = User.objects.create_user(
            phone_number='+573008887766',
            password='ProfilePass123!',
            document_type='CC',
            document_number='5556667778',
            first_name='Ana',
            last_name='Martinez',
            is_verified=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """Test retrieving user profile."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Ana')
        self.assertEqual(response.data['last_name'], 'Martinez')
        self.assertEqual(response.data['phone_number'], '+573008887766')

    def test_update_profile(self):
        """Test updating user profile."""
        response = self.client.patch(
            self.profile_url,
            {
                'first_name': 'Ana Maria',
                'city': 'Villavicencio',
                'department': 'Meta',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Ana Maria')
        self.assertEqual(self.user.city, 'Villavicencio')
        self.assertEqual(self.user.department, 'Meta')

    def test_cannot_update_readonly_fields(self):
        """Test that read-only fields cannot be updated."""
        response = self.client.patch(
            self.profile_url,
            {
                'phone_number': '+573000000000',
                'is_verified': False,
                'is_merchant': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        # Read-only fields should not change
        self.assertEqual(str(self.user.phone_number), '+573008887766')
        self.assertTrue(self.user.is_verified)
        self.assertFalse(self.user.is_merchant)

    def test_unauthenticated_profile_access(self):
        """Test that unauthenticated users cannot access profile."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
