from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.web_dashboard.views_platform import platform_app

urlpatterns = [
    path('', RedirectView.as_view(url='/app/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/wallet/', include('apps.wallet.urls')),
    path('api/v1/crypto/', include('apps.crypto.urls')),
    path('api/v1/transfers/', include('apps.transfers.urls')),
    path('api/v1/marketplace/', include('apps.marketplace.urls')),
    path('api/v1/microcredit/', include('apps.microcredit.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    # Web Dashboard
    path('dashboard/', include('apps.web_dashboard.urls')),
    # User-facing Web Platform (SPA)
    re_path(r'^app(?:/.*)?$', platform_app, name='platform'),
    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
