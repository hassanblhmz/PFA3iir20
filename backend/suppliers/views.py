from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Supplier
from .serializers import SupplierSerializer, SupplierListSerializer
from users.permissions import IsAdminOrReadOnly


class SupplierViewSet(viewsets.ModelViewSet):
    """CRUD complet pour les fournisseurs"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name', 'code', 'email', 'city']
    filterset_fields = ['status', 'country']
    ordering_fields = ['name', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return SupplierListSerializer
        return SupplierSerializer

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Historique des commandes d'un fournisseur"""
        from purchases.models import PurchaseOrder
        from purchases.serializers import PurchaseOrderListSerializer
        supplier = self.get_object()
        orders = PurchaseOrder.objects.filter(supplier=supplier).order_by('-created_at')
        serializer = PurchaseOrderListSerializer(orders, many=True)
        return Response(serializer.data)
