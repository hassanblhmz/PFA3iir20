from django.contrib import admin
from .models import (
    PurchaseRequest, PurchaseRequestLine, PurchaseOrder, PurchaseOrderLine,
    ValidationLog, Reception, SupplierRequestConversation, SupplierRequestMessage
)

class PRLineInline(admin.TabularInline):
    model = PurchaseRequestLine
    extra = 0

@admin.register(PurchaseRequest)
class PRAdmin(admin.ModelAdmin):
    list_display = ['reference', 'title', 'status', 'priority', 'requested_by', 'created_at']
    list_filter = ['status', 'priority']
    inlines = [PRLineInline]

class POLineInline(admin.TabularInline):
    model = PurchaseOrderLine
    extra = 0

@admin.register(PurchaseOrder)
class POAdmin(admin.ModelAdmin):
    list_display = ['reference', 'supplier', 'status', 'ordered_by', 'created_at']
    list_filter = ['status']
    inlines = [POLineInline]

@admin.register(ValidationLog)
class ValidationLogAdmin(admin.ModelAdmin):
    list_display = ['request', 'action', 'performed_by', 'created_at']
    list_filter = ['action']


class SupplierRequestMessageInline(admin.TabularInline):
    model = SupplierRequestMessage
    extra = 0


@admin.register(SupplierRequestConversation)
class SupplierRequestConversationAdmin(admin.ModelAdmin):
    list_display = ['purchase_request', 'supplier', 'demandeur', 'trigger', 'status', 'updated_at']
    list_filter = ['trigger', 'status', 'supplier']
    search_fields = ['purchase_request__reference', 'supplier__name', 'subject']
    inlines = [SupplierRequestMessageInline]
