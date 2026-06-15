from django.contrib import admin
from .models import (
    PurchaseRequest, PurchaseRequestLine, PurchaseOrder, PurchaseOrderLine,
    ValidationLog, Reception, SupplierConsultation, SupplierQuote,
    Notification, AuditLog, SupplierRequestConversation, SupplierRequestMessage
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
    list_display = ['reference', 'supplier', 'status', 'supplier_response_status', 'ordered_by', 'created_at']
    list_filter = ['status', 'supplier_response_status']
    inlines = [POLineInline]

@admin.register(ValidationLog)
class ValidationLogAdmin(admin.ModelAdmin):
    list_display = ['request', 'action', 'performed_by', 'created_at']
    list_filter = ['action']


@admin.register(SupplierConsultation)
class SupplierConsultationAdmin(admin.ModelAdmin):
    list_display = ['reference', 'title', 'status', 'created_by', 'deadline', 'created_at']
    list_filter = ['status']
    search_fields = ['reference', 'title']


@admin.register(SupplierQuote)
class SupplierQuoteAdmin(admin.ModelAdmin):
    list_display = ['consultation', 'supplier', 'total_amount', 'delivery_days', 'is_selected', 'created_at']
    list_filter = ['is_selected', 'supplier']


@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = ['order', 'reference', 'received_by', 'received_at']
    list_filter = ['received_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['title', 'message', 'user__email']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'entity', 'entity_id', 'user', 'created_at']
    list_filter = ['action', 'entity', 'created_at']
    search_fields = ['action', 'entity', 'description', 'user__email']


class SupplierRequestMessageInline(admin.TabularInline):
    model = SupplierRequestMessage
    extra = 0


@admin.register(SupplierRequestConversation)
class SupplierRequestConversationAdmin(admin.ModelAdmin):
    list_display = ['purchase_request', 'supplier', 'demandeur', 'trigger', 'status', 'updated_at']
    list_filter = ['trigger', 'status', 'supplier']
    search_fields = ['purchase_request__reference', 'supplier__name', 'subject']
    inlines = [SupplierRequestMessageInline]
