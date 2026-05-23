from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'full_name', 'role', 'supplier', 'department', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Informations métier', {'fields': ('role', 'supplier', 'phone', 'department')}),
    )
