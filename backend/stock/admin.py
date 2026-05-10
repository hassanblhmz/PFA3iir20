from django.contrib import admin
from .models import StockMovement
@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'type', 'quantity', 'stock_before', 'stock_after', 'performed_by', 'created_at']
    list_filter = ['type']
    search_fields = ['product__name', 'reason']
