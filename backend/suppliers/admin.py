from django.contrib import admin
from .models import Supplier
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact_name', 'email', 'city', 'status']
    list_filter = ['status', 'country']
    search_fields = ['name', 'code', 'email']
