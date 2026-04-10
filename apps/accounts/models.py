import random
import string

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    """Custom manager that uses phone_number instead of username."""

    def _create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('El numero de telefono es obligatorio.')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Un superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Un superusuario debe tener is_superuser=True.')

        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """Custom User model for LlanoPay with phone-based authentication."""

    class DocumentType(models.TextChoices):
        CC = 'CC', 'Cedula de Ciudadania'
        CE = 'CE', 'Cedula de Extranjeria'
        TI = 'TI', 'Tarjeta de Identidad'
        NIT = 'NIT', 'NIT'
        PASAPORTE = 'PASAPORTE', 'Pasaporte'

    # Remove the default username field
    username = None

    phone_number = PhoneNumberField(
        unique=True,
        verbose_name='Numero de telefono',
        help_text='Numero de telefono con codigo de pais (ej. +573001234567)',
    )
    document_type = models.CharField(
        max_length=10,
        choices=DocumentType.choices,
        default=DocumentType.CC,
        verbose_name='Tipo de documento',
    )
    document_number = models.CharField(
        max_length=20,
        verbose_name='Numero de documento',
    )
    first_name = models.CharField(max_length=150, verbose_name='Nombres')
    last_name = models.CharField(max_length=150, verbose_name='Apellidos')
    email = models.EmailField(blank=True, null=True, verbose_name='Correo electronico')
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Verificado',
        help_text='Indica si el usuario ha verificado su numero de telefono.',
    )
    is_merchant = models.BooleanField(
        default=False,
        verbose_name='Es comerciante',
        help_text='Indica si el usuario es un comerciante registrado.',
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name='Foto de perfil',
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de nacimiento',
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Ciudad',
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Departamento',
    )
    country = models.CharField(
        max_length=2,
        blank=True,
        default='CO',
        verbose_name='Pais (ISO)',
        help_text='Codigo ISO 3166-1 alpha-2 (CO, US, MX, etc)',
    )
    preferred_currency = models.CharField(
        max_length=3,
        blank=True,
        default='COP',
        verbose_name='Moneda preferida',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualizacion')

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['document_type', 'document_number', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.phone_number})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()


class OTPCode(models.Model):
    """One-time password codes for verification."""

    class Purpose(models.TextChoices):
        REGISTER = 'REGISTER', 'Registro'
        LOGIN = 'LOGIN', 'Inicio de sesion'
        TRANSFER = 'TRANSFER', 'Transferencia'
        RESET = 'RESET', 'Restablecer contrasena'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otp_codes',
        verbose_name='Usuario',
    )
    code = models.CharField(max_length=6, verbose_name='Codigo OTP')
    purpose = models.CharField(
        max_length=10,
        choices=Purpose.choices,
        verbose_name='Proposito',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')
    expires_at = models.DateTimeField(verbose_name='Fecha de expiracion')
    is_used = models.BooleanField(default=False, verbose_name='Usado')

    class Meta:
        verbose_name = 'Codigo OTP'
        verbose_name_plural = 'Codigos OTP'
        ordering = ['-created_at']

    def __str__(self):
        return f'OTP {self.code} para {self.user.phone_number} ({self.purpose})'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.digits, k=6))
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired


class KYCDocument(models.Model):
    """Know Your Customer document verification."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        APPROVED = 'APPROVED', 'Aprobado'
        REJECTED = 'REJECTED', 'Rechazado'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='kyc_documents',
        verbose_name='Usuario',
    )
    document_type = models.CharField(
        max_length=10,
        choices=User.DocumentType.choices,
        verbose_name='Tipo de documento',
    )
    front_image = models.ImageField(
        upload_to='kyc/front/',
        verbose_name='Imagen frontal',
    )
    back_image = models.ImageField(
        upload_to='kyc/back/',
        verbose_name='Imagen trasera',
    )
    selfie_image = models.ImageField(
        upload_to='kyc/selfie/',
        verbose_name='Selfie',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado',
    )
    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de revision',
    )
    reviewer_notes = models.TextField(
        blank=True,
        default='',
        verbose_name='Notas del revisor',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')

    class Meta:
        verbose_name = 'Documento KYC'
        verbose_name_plural = 'Documentos KYC'
        ordering = ['-created_at']

    def __str__(self):
        return f'KYC {self.document_type} - {self.user.phone_number} ({self.status})'
