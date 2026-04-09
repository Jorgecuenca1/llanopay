import uuid

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class MerchantCategory(models.Model):
    """Categorias de comerciantes en el marketplace."""

    name = models.CharField(max_length=100, verbose_name='nombre')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='slug')
    icon = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='icono',
        help_text='Nombre del icono (ej. mdi-store, fa-shop)',
    )
    description = models.TextField(blank=True, default='', verbose_name='descripcion')
    is_active = models.BooleanField(default=True, verbose_name='activa')
    order = models.IntegerField(default=0, verbose_name='orden')

    class Meta:
        verbose_name = 'categoria de comerciante'
        verbose_name_plural = 'categorias de comerciantes'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Merchant(models.Model):
    """Comerciante registrado en el marketplace regional."""

    class Department(models.TextChoices):
        META = 'META', 'Meta'
        CASANARE = 'CASANARE', 'Casanare'
        ARAUCA = 'ARAUCA', 'Arauca'
        VICHADA = 'VICHADA', 'Vichada'
        GUAINIA = 'GUAINIA', 'Guainia'
        GUAVIARE = 'GUAVIARE', 'Guaviare'
        VAUPES = 'VAUPES', 'Vaupes'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='merchant_profile',
        verbose_name='usuario',
    )
    business_name = models.CharField(max_length=200, verbose_name='nombre del negocio')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='slug')
    category = models.ForeignKey(
        MerchantCategory,
        on_delete=models.PROTECT,
        related_name='merchants',
        verbose_name='categoria',
    )
    description = models.TextField(blank=True, default='', verbose_name='descripcion')
    address = models.CharField(max_length=300, verbose_name='direccion')
    city = models.CharField(max_length=100, verbose_name='ciudad')
    department = models.CharField(
        max_length=10,
        choices=Department.choices,
        verbose_name='departamento',
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='latitud',
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='longitud',
    )
    phone = models.CharField(max_length=20, verbose_name='telefono')
    whatsapp = models.CharField(max_length=20, blank=True, default='', verbose_name='whatsapp')
    logo = models.ImageField(
        upload_to='marketplace/logos/',
        blank=True,
        null=True,
        verbose_name='logo',
    )
    cover_image = models.ImageField(
        upload_to='marketplace/covers/',
        blank=True,
        null=True,
        verbose_name='imagen de portada',
    )
    accepts_llo = models.BooleanField(default=True, verbose_name='acepta LLO')
    accepts_cop = models.BooleanField(default=True, verbose_name='acepta COP')
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.5,
        verbose_name='tasa de comision (%)',
    )
    is_verified = models.BooleanField(default=False, verbose_name='verificado')
    is_active = models.BooleanField(default=True, verbose_name='activo')
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        verbose_name='calificacion',
    )
    total_reviews = models.IntegerField(default=0, verbose_name='total de resenas')
    total_sales = models.IntegerField(default=0, verbose_name='total de ventas')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='fecha de actualizacion')

    class Meta:
        verbose_name = 'comerciante'
        verbose_name_plural = 'comerciantes'
        ordering = ['-rating', '-total_sales']
        indexes = [
            models.Index(fields=['city', 'department'], name='idx_merchant_location'),
            models.Index(fields=['category', 'is_active'], name='idx_merchant_category'),
        ]

    def __str__(self):
        return f'{self.business_name} ({self.city}, {self.get_department_display()})'


class MerchantPayment(models.Model):
    """Pagos realizados a comerciantes a traves del marketplace."""

    class Currency(models.TextChoices):
        COP = 'COP', 'Peso colombiano'
        LLO = 'LLO', 'LlanoCoin'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        COMPLETED = 'COMPLETED', 'Completado'
        FAILED = 'FAILED', 'Fallido'

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='comerciante',
    )
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='merchant_payments',
        verbose_name='pagador',
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='monto')
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        verbose_name='moneda',
    )
    commission_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='monto de comision',
    )
    reference = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='referencia')
    description = models.TextField(blank=True, default='', verbose_name='descripcion')
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='estado',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='fecha de completado',
    )

    class Meta:
        verbose_name = 'pago a comerciante'
        verbose_name_plural = 'pagos a comerciantes'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'Pago {self.reference} - {self.currency} {self.amount} '
            f'a {self.merchant.business_name} ({self.get_status_display()})'
        )


class MerchantReview(models.Model):
    """Resenas de usuarios para comerciantes."""

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='comerciante',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='merchant_reviews',
        verbose_name='usuario',
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='calificacion',
    )
    comment = models.TextField(blank=True, default='', verbose_name='comentario')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')

    class Meta:
        verbose_name = 'resena de comerciante'
        verbose_name_plural = 'resenas de comerciantes'
        ordering = ['-created_at']
        unique_together = ['merchant', 'user']

    def __str__(self):
        return f'Resena de {self.user} para {self.merchant.business_name} - {self.rating}/5'


class Promotion(models.Model):
    """Promociones publicadas por comerciantes."""

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name='promotions',
        verbose_name='comerciante',
    )
    title = models.CharField(max_length=200, verbose_name='titulo')
    description = models.TextField(verbose_name='descripcion')
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='porcentaje de descuento',
    )
    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='monto de descuento',
    )
    start_date = models.DateTimeField(verbose_name='fecha de inicio')
    end_date = models.DateTimeField(verbose_name='fecha de fin')
    is_active = models.BooleanField(default=True, verbose_name='activa')
    image = models.ImageField(
        upload_to='marketplace/promotions/',
        blank=True,
        null=True,
        verbose_name='imagen',
    )

    class Meta:
        verbose_name = 'promocion'
        verbose_name_plural = 'promociones'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.title} - {self.merchant.business_name}'
