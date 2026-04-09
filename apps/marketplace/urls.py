from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'reviews', views.MerchantReviewViewSet, basename='merchant-reviews')
router.register(r'promotions', views.PromotionViewSet, basename='promotions')

app_name = 'marketplace'

urlpatterns = [
    # Categorias
    path('categories/', views.MerchantCategoryListView.as_view(), name='category-list'),
    # Comerciantes
    path('merchants/', views.MerchantListView.as_view(), name='merchant-list'),
    path('merchants/register/', views.MerchantRegistrationView.as_view(), name='merchant-register'),
    path('merchants/dashboard/', views.MerchantDashboardView.as_view(), name='merchant-dashboard'),
    path('merchants/nearby/', views.NearbyMerchantsView.as_view(), name='merchant-nearby'),
    path('merchants/<slug:slug>/', views.MerchantDetailView.as_view(), name='merchant-detail'),
    # Pagos
    path('payments/', views.MerchantPaymentView.as_view(), name='merchant-payment'),
    # Router (reviews, promotions)
    path('', include(router.urls)),
]
