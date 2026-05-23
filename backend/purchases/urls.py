from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PurchaseRequestViewSet, PurchaseOrderViewSet, ReceptionViewSet,
    SupplierRequestConversationViewSet, DashboardView
)

router = DefaultRouter()
router.register(r'requests', PurchaseRequestViewSet, basename='purchase-request')
router.register(r'orders', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'receptions', ReceptionViewSet, basename='reception')
router.register(r'supplier-conversations', SupplierRequestConversationViewSet, basename='supplier-conversation')
router.register(r'dashboard', DashboardView, basename='dashboard')

urlpatterns = [path('', include(router.urls))]
