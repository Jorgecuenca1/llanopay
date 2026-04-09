from decimal import Decimal

from django.db import transaction
from django.db.models import Avg, F, Q
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Merchant,
    MerchantCategory,
    MerchantPayment,
    MerchantReview,
    Promotion,
)
from .serializers import (
    MerchantCategorySerializer,
    MerchantCreateUpdateSerializer,
    MerchantDetailSerializer,
    MerchantListSerializer,
    MerchantPaymentSerializer,
    MerchantReviewSerializer,
    PromotionSerializer,
)


class MerchantCategoryListView(generics.ListAPIView):
    """Listar todas las categorias de comerciantes activas."""

    queryset = MerchantCategory.objects.filter(is_active=True)
    serializer_class = MerchantCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class MerchantListView(generics.ListAPIView):
    """Listar comerciantes con busqueda y filtros por categoria, ciudad y departamento."""

    serializer_class = MerchantListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Merchant.objects.filter(is_active=True).select_related('category')
        # Filtro por categoria
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        # Filtro por ciudad
        city = self.request.query_params.get('city')
        if city:
            qs = qs.filter(city__icontains=city)
        # Filtro por departamento
        department = self.request.query_params.get('department')
        if department:
            qs = qs.filter(department=department.upper())
        # Busqueda por nombre o descripcion
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(business_name__icontains=search) | Q(description__icontains=search)
            )
        # Filtro por tipo de moneda aceptada
        accepts = self.request.query_params.get('accepts')
        if accepts == 'LLO':
            qs = qs.filter(accepts_llo=True)
        elif accepts == 'COP':
            qs = qs.filter(accepts_cop=True)
        return qs


class MerchantDetailView(generics.RetrieveAPIView):
    """Ver detalle de un comerciante por slug."""

    serializer_class = MerchantDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Merchant.objects.filter(is_active=True).select_related('category', 'user')


class MerchantRegistrationView(APIView):
    """Registrar al usuario autenticado como comerciante."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'merchant_profile'):
            return Response(
                {'detail': 'Ya estas registrado como comerciante.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = MerchantCreateUpdateSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        merchant = serializer.save()
        # Marcar usuario como comerciante
        request.user.is_merchant = True
        request.user.save(update_fields=['is_merchant'])
        return Response(
            MerchantDetailSerializer(merchant).data,
            status=status.HTTP_201_CREATED,
        )


class MerchantDashboardView(APIView):
    """Dashboard con estadisticas del comerciante autenticado."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            merchant = request.user.merchant_profile
        except Merchant.DoesNotExist:
            return Response(
                {'detail': 'No estas registrado como comerciante.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        total_revenue = MerchantPayment.objects.filter(
            merchant=merchant, status='COMPLETED'
        )
        total_cop = sum(
            p.amount for p in total_revenue.filter(currency='COP')
        )
        total_llo = sum(
            p.amount for p in total_revenue.filter(currency='LLO')
        )
        total_commissions = sum(p.commission_amount for p in total_revenue)

        pending_payments = MerchantPayment.objects.filter(
            merchant=merchant, status='PENDING'
        ).count()

        recent_payments = MerchantPaymentSerializer(
            MerchantPayment.objects.filter(merchant=merchant).order_by('-created_at')[:10],
            many=True,
        ).data

        active_promotions = merchant.promotions.filter(
            is_active=True, end_date__gte=timezone.now()
        ).count()

        return Response({
            'merchant': MerchantListSerializer(merchant).data,
            'stats': {
                'total_sales': merchant.total_sales,
                'total_reviews': merchant.total_reviews,
                'rating': str(merchant.rating),
                'total_revenue_cop': str(total_cop),
                'total_revenue_llo': str(total_llo),
                'total_commissions': str(total_commissions),
                'pending_payments': pending_payments,
                'active_promotions': active_promotions,
            },
            'recent_payments': recent_payments,
        })


class MerchantPaymentView(APIView):
    """Realizar un pago a un comerciante (operacion atomica)."""

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = MerchantPaymentSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        merchant = serializer.validated_data['merchant']
        amount = serializer.validated_data['amount']
        currency = serializer.validated_data['currency']

        # Calcular comision
        commission = (amount * merchant.commission_rate / Decimal('100')).quantize(
            Decimal('0.01')
        )

        # Verificar saldo del pagador
        payer_wallet = request.user.wallet
        if currency == 'COP':
            if payer_wallet.balance_cop < amount:
                return Response(
                    {'detail': 'Saldo COP insuficiente.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            payer_wallet.withdraw_cop(amount)
            merchant.user.wallet.deposit_cop(amount - commission)
        elif currency == 'LLO':
            if payer_wallet.balance_llo < amount:
                return Response(
                    {'detail': 'Saldo LLO insuficiente.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            payer_wallet.withdraw_llo(amount)
            merchant.user.wallet.deposit_llo(amount - commission)

        # Crear registro del pago
        payment = MerchantPayment.objects.create(
            merchant=merchant,
            payer=request.user,
            amount=amount,
            currency=currency,
            commission_amount=commission,
            description=serializer.validated_data.get('description', ''),
            status=MerchantPayment.Status.COMPLETED,
            completed_at=timezone.now(),
        )

        # Actualizar contador de ventas del comerciante
        Merchant.objects.filter(pk=merchant.pk).update(
            total_sales=F('total_sales') + 1
        )

        return Response(
            MerchantPaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class MerchantReviewViewSet(viewsets.ModelViewSet):
    """Listar y crear resenas para comerciantes."""

    serializer_class = MerchantReviewSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = MerchantReview.objects.select_related('user', 'merchant')
        merchant_id = self.request.query_params.get('merchant')
        if merchant_id:
            qs = qs.filter(merchant_id=merchant_id)
        return qs

    def perform_create(self, serializer):
        review = serializer.save()
        # Recalcular calificacion promedio del comerciante
        merchant = review.merchant
        avg = MerchantReview.objects.filter(merchant=merchant).aggregate(
            avg_rating=Avg('rating')
        )
        review_count = MerchantReview.objects.filter(merchant=merchant).count()
        Merchant.objects.filter(pk=merchant.pk).update(
            rating=avg['avg_rating'] or 0,
            total_reviews=review_count,
        )


class PromotionViewSet(viewsets.ModelViewSet):
    """CRUD de promociones. Solo el dueno del comerciante puede gestionar."""

    serializer_class = PromotionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'merchant_profile'):
            return Promotion.objects.filter(merchant=user.merchant_profile)
        return Promotion.objects.none()

    def perform_create(self, serializer):
        merchant = self.request.user.merchant_profile
        serializer.save(merchant=merchant)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            qs = Promotion.objects.filter(is_active=True).select_related('merchant')
            merchant_id = self.request.query_params.get('merchant')
            if merchant_id:
                qs = qs.filter(merchant_id=merchant_id)
            return qs
        # For create/update/delete, only the merchant owner
        user = self.request.user
        if hasattr(user, 'merchant_profile'):
            return Promotion.objects.filter(merchant=user.merchant_profile)
        return Promotion.objects.none()


class NearbyMerchantsView(APIView):
    """Buscar comerciantes cercanos por latitud y longitud.

    Usa una aproximacion simple de distancia basada en diferencia
    de coordenadas (bounding box) para evitar dependencia de PostGIS.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            lat = Decimal(request.query_params.get('lat', ''))
            lng = Decimal(request.query_params.get('lng', ''))
        except Exception:
            return Response(
                {'detail': 'Parametros lat y lng son requeridos y deben ser numericos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Radio en grados (~0.01 grado aprox 1.1 km en el ecuador)
        try:
            radius = Decimal(request.query_params.get('radius', '0.05'))
        except Exception:
            radius = Decimal('0.05')

        merchants = Merchant.objects.filter(
            is_active=True,
            latitude__isnull=False,
            longitude__isnull=False,
            latitude__gte=lat - radius,
            latitude__lte=lat + radius,
            longitude__gte=lng - radius,
            longitude__lte=lng + radius,
        ).select_related('category')

        serializer = MerchantListSerializer(merchants, many=True)
        return Response({
            'lat': str(lat),
            'lng': str(lng),
            'radius': str(radius),
            'count': merchants.count(),
            'results': serializer.data,
        })
