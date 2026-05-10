from rest_framework import serializers
from .models import StockMovement
from products.serializers import ProductListSerializer


class StockMovementSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.full_name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_detail', 'type', 'type_display',
            'quantity', 'stock_before', 'stock_after',
            'reference', 'reason', 'performed_by', 'performed_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'stock_before', 'stock_after', 'created_at']


class StockAdjustmentSerializer(serializers.Serializer):
    """Serializer pour un ajustement manuel du stock"""
    product = serializers.PrimaryKeyRelatedField(queryset=__import__('products.models', fromlist=['Product']).Product.objects.all())
    type = serializers.ChoiceField(choices=StockMovement.TYPE_CHOICES)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField(max_length=200)
    reference = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate(self, attrs):
        quantity = attrs.get('quantity')
        move_type = attrs.get('type')
        if move_type in ['entree', 'sortie'] and quantity <= 0:
            raise serializers.ValidationError({'quantity': 'La quantite doit etre superieure a 0.'})
        if move_type == 'ajustement' and quantity < 0:
            raise serializers.ValidationError({'quantity': 'Le stock ajuste ne peut pas etre negatif.'})
        return attrs
