from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F

from .models import StockMovement
from .serializers import StockMovementSerializer, StockAdjustmentSerializer
from products.models import Product
from products.serializers import ProductListSerializer
from users.permissions import IsMagasinier


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """Consultation des mouvements de stock"""
    queryset = StockMovement.objects.select_related('product', 'performed_by')
    serializer_class = StockMovementSerializer
    filterset_fields = ['product', 'type']
    search_fields = ['product__name', 'product__code', 'reference', 'reason']
    ordering_fields = ['created_at']

    @action(detail=False, methods=['post'], permission_classes=[IsMagasinier])
    def adjust(self, request):
        """Ajustement manuel du stock"""
        serializer = StockAdjustmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        product = data['product']
        quantity = data['quantity']
        move_type = data['type']

        stock_before = product.current_stock

        if move_type == 'entree':
            product.current_stock += quantity
        elif move_type == 'sortie':
            if product.current_stock < quantity:
                return Response({'error': 'Stock insuffisant.'}, status=400)
            product.current_stock -= quantity
        elif move_type == 'ajustement':
            product.current_stock = quantity  # Ajustement direct à la valeur

        product.save()

        movement = StockMovement.objects.create(
            product=product,
            type=move_type,
            quantity=quantity,
            stock_before=stock_before,
            stock_after=product.current_stock,
            reason=data.get('reason', ''),
            reference=data.get('reference', ''),
            performed_by=request.user
        )

        return Response(StockMovementSerializer(movement).data, status=201)

    @action(detail=False, methods=['get'])
    def critical_products(self, request):
        """Articles en stock critique"""
        products = Product.objects.filter(
            current_stock__lte=F('min_stock'), is_active=True
        ).order_by('current_stock')
        serializer = ProductListSerializer(products, many=True)
        return Response({
            'count': products.count(),
            'results': serializer.data
        })
