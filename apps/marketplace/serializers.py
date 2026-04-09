from decimal import Decimal

from django.utils.text import slugify
from rest_framework import serializers

from .models import (
    MerchantCategory,
    Merchant,
    MerchantPayment,
    MerchantReview,
    Promotion,
)


class MerchantCategorySerializer(serializers.ModelSerializer):
    merchant_count = serializers.SerializerMethodField()

    class Meta:
        model = MerchantCategory
        fields = ['id', 'name', 'slug', 'icon', 'description', 'merchant_count']

    def get_merchant_count(self, obj):
        return obj.merchants.filter(is_active=True).count()


class MerchantListSerializer(serializers.ModelSerializer):
    """Serializador resumido para listados de comerciantes."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    department_display = serializers.CharField(
        source='get_department_display', read_only=True
    )

    class Meta:
        model = Merchant
        fields = [
            'id',
            'business_name',
            'slug',
            'category',
            'category_name',
            'city',
            'department',
            'department_display',
            'logo',
            'accepts_llo',
            'accepts_cop',
            'is_verified',
            'rating',
            'total_reviews',
            'total_sales',
        ]


class MerchantDetailSerializer(serializers.ModelSerializer):
    """Serializador completo para detalle de comerciante."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    department_display = serializers.CharField(
        source='get_department_display', read_only=True
    )
    owner_name = serializers.CharField(source='user.full_name', read_only=True)
    promotions = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Merchant
        fields = [
            'id',
            'business_name',
            'slug',
            'category',
            'category_name',
            'description',
            'address',
            'city',
            'department',
            'department_display',
            'latitude',
            'longitude',
            'phone',
            'whatsapp',
            'logo',
            'cover_image',
            'accepts_llo',
            'accepts_cop',
            'is_verified',
            'rating',
            'total_reviews',
            'total_sales',
            'owner_name',
            'promotions',
            'recent_reviews',
            'created_at',
        ]

    def get_promotions(self, obj):
        active_promos = obj.promotions.filter(is_active=True)[:5]
        return PromotionSerializer(active_promos, many=True).data

    def get_recent_reviews(self, obj):
        reviews = obj.reviews.all()[:5]
        return MerchantReviewSerializer(reviews, many=True).data


class MerchantCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializador para registro y actualizacion de comerciantes."""

    class Meta:
        model = Merchant
        fields = [
            'business_name',
            'category',
            'description',
            'address',
            'city',
            'department',
            'latitude',
            'longitude',
            'phone',
            'whatsapp',
            'logo',
            'cover_image',
            'accepts_llo',
            'accepts_cop',
        ]

    def validate_business_name(self, value):
        slug = slugify(value)
        qs = Merchant.objects.filter(slug=slug)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'Ya existe un comerciante con un nombre similar.'
            )
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['slug'] = slugify(validated_data['business_name'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'business_name' in validated_data:
            validated_data['slug'] = slugify(validated_data['business_name'])
        return super().update(instance, validated_data)


class MerchantPaymentSerializer(serializers.ModelSerializer):
    """Serializador para crear pagos a comerciantes."""

    class Meta:
        model = MerchantPayment
        fields = [
            'id',
            'merchant',
            'amount',
            'currency',
            'commission_amount',
            'reference',
            'description',
            'status',
            'created_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'commission_amount',
            'reference',
            'status',
            'created_at',
            'completed_at',
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('El monto debe ser mayor a cero.')
        return value

    def validate(self, attrs):
        merchant = attrs.get('merchant')
        currency = attrs.get('currency')
        if currency == 'LLO' and not merchant.accepts_llo:
            raise serializers.ValidationError(
                {'currency': 'Este comerciante no acepta LlanoCoins.'}
            )
        if currency == 'COP' and not merchant.accepts_cop:
            raise serializers.ValidationError(
                {'currency': 'Este comerciante no acepta pesos colombianos.'}
            )
        if not merchant.is_active:
            raise serializers.ValidationError(
                {'merchant': 'Este comerciante no esta activo.'}
            )
        return attrs


class MerchantReviewSerializer(serializers.ModelSerializer):
    """Serializador para resenas de comerciantes."""

    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = MerchantReview
        fields = ['id', 'merchant', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                'La calificacion debe estar entre 1 y 5.'
            )
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        merchant = attrs.get('merchant')
        if request and request.user == merchant.user:
            raise serializers.ValidationError(
                'No puedes dejar una resena en tu propio negocio.'
            )
        if request and MerchantReview.objects.filter(
            merchant=merchant, user=request.user
        ).exists():
            raise serializers.ValidationError(
                'Ya dejaste una resena para este comerciante.'
            )
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PromotionSerializer(serializers.ModelSerializer):
    """Serializador para promociones de comerciantes."""

    merchant_name = serializers.CharField(
        source='merchant.business_name', read_only=True
    )

    class Meta:
        model = Promotion
        fields = [
            'id',
            'merchant',
            'merchant_name',
            'title',
            'description',
            'discount_percentage',
            'discount_amount',
            'start_date',
            'end_date',
            'is_active',
            'image',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                {'end_date': 'La fecha de fin debe ser posterior a la fecha de inicio.'}
            )
        discount_pct = attrs.get('discount_percentage')
        discount_amt = attrs.get('discount_amount')
        if not discount_pct and not discount_amt:
            raise serializers.ValidationError(
                'Debe especificar un porcentaje o monto de descuento.'
            )
        return attrs
