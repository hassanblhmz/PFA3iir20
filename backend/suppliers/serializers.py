from rest_framework import serializers
from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    orders_count = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_orders_count(self, obj):
        return obj.purchaseorder_set.count()


class SupplierListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    class Meta:
        model = Supplier
        fields = ['id', 'code', 'name', 'contact_name', 'email', 'phone', 'status', 'city']
