from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductListSerializer
from users.permissions import IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').prefetch_related('suppliers')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['category', 'is_active', 'unit']
    ordering_fields = ['name', 'current_stock', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Articles en stock critique"""
        from django.db.models import F
        products = Product.objects.filter(
            current_stock__lte=F('min_stock'),
            is_active=True
        ).select_related('category')
        serializer = ProductListSerializer(products, many=True)
        return Response({'count': products.count(), 'results': serializer.data})
