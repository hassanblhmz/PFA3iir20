from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'unit_price', 'current_stock', 'min_stock', 'stock_status']
    list_filter = ['category', 'is_active']
    search_fields = ['code', 'name']
