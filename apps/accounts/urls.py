from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'kyc', views.KYCDocumentViewSet, basename='kyc')

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('request-otp/', views.RequestOTPView.as_view(), name='request-otp'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('', include(router.urls)),
]
