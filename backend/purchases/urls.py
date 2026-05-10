from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PurchaseRequestViewSet, PurchaseOrderViewSet, ReceptionViewSet, DashboardView

router = DefaultRouter()
router.register(r'requests', PurchaseRequestViewSet, basename='purchase-request')
router.register(r'orders', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'receptions', ReceptionViewSet, basename='reception')
router.register(r'dashboard', DashboardView, basename='dashboard')

urlpatterns = [path('', include(router.urls))]
