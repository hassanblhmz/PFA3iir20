"""
URL Configuration principale - PFA Gestion Achats
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth JWT
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Apps
    path('api/users/', include('users.urls')),
    path('api/suppliers/', include('suppliers.urls')),
    path('api/products/', include('products.urls')),
    path('api/purchases/', include('purchases.urls')),
    path('api/stock/', include('stock.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
