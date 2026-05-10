from rest_framework import serializers
from .models import Category, Product
from suppliers.serializers import SupplierListSerializer


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products_count', 'created_at']

    def get_products_count(self, obj):
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_critical = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()
    suppliers_detail = SupplierListSerializer(source='suppliers', many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'code', 'name', 'description', 'category', 'category_name',
            'unit', 'unit_price', 'current_stock', 'min_stock', 'max_stock',
            'is_critical', 'stock_status', 'suppliers', 'suppliers_detail',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_critical = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'category', 'category_name', 'unit',
                  'unit_price', 'current_stock', 'min_stock', 'is_critical',
                  'stock_status', 'is_active']
