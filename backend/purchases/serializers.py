from django.db import transaction
from rest_framework import serializers
from .models import (
    PurchaseRequest, PurchaseRequestLine, ValidationLog,
    PurchaseOrder, PurchaseOrderLine, Reception, ReceptionLine,
    SupplierConsultation, SupplierQuote, Notification, AuditLog,
    SupplierRequestConversation, SupplierRequestMessage
)
from products.serializers import ProductListSerializer
from suppliers.serializers import SupplierSerializer
from stock.models import StockMovement


ALLOWED_RECEPTION_ORDER_STATUSES = ['envoyee', 'confirmee', 'expediee', 'recue_partielle']


def create_audit_log(user, action, entity, entity_id=None, description=''):
    """Create a minimal audit entry without blocking the business action."""
    try:
        AuditLog.objects.create(
            user=user if getattr(user, 'is_authenticated', False) else None,
            action=action,
            entity=entity,
            entity_id=entity_id,
            description=description,
        )
    except Exception:
        pass


class PurchaseRequestLineSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseRequestLine
        fields = ['id', 'product', 'product_detail', 'quantity', 'unit_price', 'total_price', 'notes']

    def validate(self, attrs):
        if attrs.get('quantity', 0) <= 0:
            raise serializers.ValidationError({'quantity': 'La quantite doit etre superieure a 0.'})
        if attrs.get('unit_price', 0) < 0:
            raise serializers.ValidationError({'unit_price': 'Le prix unitaire ne peut pas etre negatif.'})
        return attrs


class ValidationLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.full_name', read_only=True)

    class Meta:
        model = ValidationLog
        fields = ['id', 'action', 'performed_by', 'performed_by_name', 'comment',
                  'old_status', 'new_status', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_name', 'action', 'entity', 'entity_id', 'description', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'link', 'is_read', 'created_at']


class SupplierQuoteSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    score = serializers.ReadOnlyField()

    class Meta:
        model = SupplierQuote
        fields = [
            'id', 'consultation', 'supplier', 'supplier_name', 'reference',
            'total_amount', 'delivery_days', 'availability', 'quality_score',
            'score', 'notes', 'is_selected', 'created_at'
        ]
        read_only_fields = ['id', 'is_selected', 'created_at']

    def validate(self, attrs):
        if attrs.get('total_amount', 0) < 0:
            raise serializers.ValidationError({'total_amount': 'Le montant ne peut pas etre negatif.'})
        if not 1 <= attrs.get('quality_score', 3) <= 5:
            raise serializers.ValidationError({'quality_score': 'La note qualite doit etre entre 1 et 5.'})
        return attrs


class SupplierConsultationSerializer(serializers.ModelSerializer):
    quotes = SupplierQuoteSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    best_quote_id = serializers.IntegerField(source='best_quote.id', read_only=True)

    class Meta:
        model = SupplierConsultation
        fields = [
            'id', 'reference', 'purchase_request', 'title', 'description',
            'suppliers', 'status', 'created_by', 'created_by_name',
            'selected_quote', 'best_quote_id', 'deadline', 'quotes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reference', 'created_by', 'selected_quote', 'created_at', 'updated_at']


class SupplierRequestMessageSerializer(serializers.ModelSerializer):
    sender_user_name = serializers.CharField(source='sender_user.full_name', read_only=True)
    sender_supplier_name = serializers.CharField(source='sender_supplier.name', read_only=True)

    class Meta:
        model = SupplierRequestMessage
        fields = [
            'id', 'conversation', 'sender_type', 'sender_user', 'sender_user_name',
            'sender_supplier', 'sender_supplier_name', 'body', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        conversation = attrs.get('conversation') or getattr(self.instance, 'conversation', None)
        sender_type = attrs.get('sender_type') or getattr(self.instance, 'sender_type', None)
        sender_user = attrs.get('sender_user') or getattr(self.instance, 'sender_user', None)
        sender_supplier = attrs.get('sender_supplier') or getattr(self.instance, 'sender_supplier', None)
        body = attrs.get('body') or getattr(self.instance, 'body', '')

        if not body or not body.strip():
            raise serializers.ValidationError({'body': 'Le message ne peut pas etre vide.'})
        if conversation and conversation.status == 'cloturee':
            raise serializers.ValidationError({'conversation': 'Impossible de repondre a une conversation cloturee.'})
        if sender_type == 'demandeur':
            if not sender_user:
                raise serializers.ValidationError({'sender_user': 'Un message demandeur doit etre lie a un utilisateur.'})
            if sender_supplier:
                raise serializers.ValidationError({'sender_supplier': 'Un message demandeur ne doit pas etre lie a un fournisseur.'})
            if conversation and sender_user.id != conversation.demandeur_id:
                raise serializers.ValidationError({'sender_user': 'Seul le demandeur de la conversation peut envoyer ce message.'})
        if sender_type == 'fournisseur':
            if not sender_supplier:
                raise serializers.ValidationError({'sender_supplier': 'Un message fournisseur doit etre lie a un fournisseur.'})
            if sender_user:
                raise serializers.ValidationError({'sender_user': 'Un message fournisseur ne doit pas etre lie a un utilisateur.'})
            if conversation and sender_supplier.id != conversation.supplier_id:
                raise serializers.ValidationError({'sender_supplier': 'Seul le fournisseur de la conversation peut envoyer ce message.'})
        return attrs


class SupplierRequestConversationSerializer(serializers.ModelSerializer):
    messages = SupplierRequestMessageSerializer(many=True, read_only=True)
    supplier_detail = SupplierSerializer(source='supplier', read_only=True)
    demandeur_name = serializers.CharField(source='demandeur.full_name', read_only=True)
    product_detail = ProductListSerializer(source='product', read_only=True)
    trigger_display = serializers.CharField(source='get_trigger_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SupplierRequestConversation
        fields = [
            'id', 'purchase_request', 'request_line', 'supplier', 'supplier_detail',
            'demandeur', 'demandeur_name', 'product_detail', 'trigger',
            'trigger_display', 'status', 'status_display', 'subject',
            'messages', 'opened_at', 'updated_at', 'closed_at'
        ]
        read_only_fields = ['id', 'demandeur', 'opened_at', 'updated_at', 'closed_at']

    def validate(self, attrs):
        request_line = attrs.get('request_line') or getattr(self.instance, 'request_line', None)
        purchase_request = attrs.get('purchase_request') or getattr(self.instance, 'purchase_request', None)
        if request_line and purchase_request and request_line.request_id != purchase_request.id:
            raise serializers.ValidationError({
                'request_line': 'La ligne doit appartenir a la demande selectionnee.'
            })

        product = request_line.product if request_line else None
        if not product:
            return attrs

        expected_trigger = SupplierRequestConversation.trigger_for_product(product)
        trigger = attrs.get('trigger') or getattr(self.instance, 'trigger', '')
        if trigger and trigger != expected_trigger:
            raise serializers.ValidationError({
                'trigger': f"Le declencheur doit etre '{expected_trigger}' pour cet article."
            })
        attrs['trigger'] = expected_trigger
        return attrs


class PurchaseRequestSerializer(serializers.ModelSerializer):
    lines = PurchaseRequestLineSerializer(many=True)
    logs = ValidationLogSerializer(many=True, read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    total_amount = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = [
            'id', 'reference', 'title', 'status', 'status_display', 'priority',
            'requested_by', 'requested_by_name', 'department',
            'needed_date', 'notes', 'lines', 'logs',
            'total_amount', 'created_at', 'updated_at', 'submitted_at'
        ]
        read_only_fields = [
            'id', 'reference', 'requested_by', 'created_at', 'updated_at',
            'submitted_at'
        ]

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        request = PurchaseRequest.objects.create(**validated_data)
        for line_data in lines_data:
            PurchaseRequestLine.objects.create(request=request, **line_data)
        return request

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if lines_data is not None:
            instance.lines.all().delete()
            for line_data in lines_data:
                PurchaseRequestLine.objects.create(request=instance, **line_data)
        return instance


class PurchaseRequestListSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    total_amount = serializers.ReadOnlyField()
    lines_count = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseRequest
        fields = [
            'id', 'reference', 'title', 'status', 'priority',
            'requested_by_name', 'department', 'needed_date',
            'total_amount', 'lines_count', 'created_at'
        ]

    def get_lines_count(self, obj):
        return obj.lines.count()


class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)
    total_price = serializers.ReadOnlyField()
    is_fully_received = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseOrderLine
        fields = [
            'id', 'product', 'product_detail', 'quantity_ordered',
            'quantity_received', 'unit_price', 'total_price', 'is_fully_received', 'notes'
        ]

    def validate(self, attrs):
        if attrs.get('quantity_ordered', 0) <= 0:
            raise serializers.ValidationError({'quantity_ordered': 'La quantite commandee doit etre superieure a 0.'})
        if attrs.get('unit_price', 0) < 0:
            raise serializers.ValidationError({'unit_price': 'Le prix unitaire ne peut pas etre negatif.'})
        return attrs


class PurchaseOrderSerializer(serializers.ModelSerializer):
    order_lines = PurchaseOrderLineSerializer(many=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    ordered_by_name = serializers.CharField(source='ordered_by.full_name', read_only=True)
    total_amount = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'reference', 'purchase_request', 'supplier', 'supplier_name',
            'status', 'status_display', 'ordered_by', 'ordered_by_name',
            'expected_date', 'notes', 'supplier_response_status',
            'supplier_quote_amount', 'supplier_delivery_date',
            'supplier_document_reference', 'supplier_note',
            'supplier_responded_at', 'order_lines',
            'total_amount', 'created_at', 'updated_at', 'sent_at'
        ]
        read_only_fields = [
            'id', 'reference', 'ordered_by', 'created_at', 'updated_at',
            'sent_at'
        ]

    def create(self, validated_data):
        purchase_request = validated_data.get('purchase_request')
        if purchase_request is None:
            raise serializers.ValidationError({
                'purchase_request': 'Une commande doit etre liee a une demande d achat validee.'
            })
        if purchase_request.status != 'valide':
            raise serializers.ValidationError({
                'purchase_request': 'Seule une demande validee peut generer une commande.'
            })
        if hasattr(purchase_request, 'order'):
            raise serializers.ValidationError({
                'purchase_request': 'Cette demande a deja ete convertie en commande.'
            })
        lines_data = validated_data.pop('order_lines')
        with transaction.atomic():
            order = PurchaseOrder.objects.create(**validated_data)
            for line_data in lines_data:
                PurchaseOrderLine.objects.create(order=order, **line_data)
            purchase_request.status = 'commande'
            purchase_request.save(update_fields=['status', 'updated_at'])
        return order


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    total_amount = serializers.ReadOnlyField()
    lines_count = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'reference', 'supplier', 'supplier_name', 'status',
            'supplier_response_status', 'supplier_quote_amount',
            'supplier_delivery_date', 'total_amount', 'lines_count',
            'expected_date', 'created_at'
        ]

    def get_lines_count(self, obj):
        return obj.order_lines.count()


class ReceptionLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceptionLine
        fields = ['id', 'order_line', 'quantity_received', 'notes']

    def validate(self, attrs):
        if attrs.get('quantity_received', 0) <= 0:
            raise serializers.ValidationError({'quantity_received': 'La quantite recue doit etre superieure a 0.'})
        return attrs


class ReceptionSerializer(serializers.ModelSerializer):
    lines = ReceptionLineSerializer(many=True)
    received_by_name = serializers.CharField(source='received_by.full_name', read_only=True)

    class Meta:
        model = Reception
        fields = ['id', 'order', 'received_by', 'received_by_name',
                  'reference', 'notes', 'lines', 'received_at']
        read_only_fields = ['id', 'received_by', 'received_at']

    def validate(self, attrs):
        order = attrs.get('order')
        if order.status not in ALLOWED_RECEPTION_ORDER_STATUSES:
            raise serializers.ValidationError({
                'order': 'Une reception est autorisee uniquement pour une commande envoyee, confirmee ou partiellement recue.'
            })
        lines = attrs.get('lines', [])
        if not lines:
            raise serializers.ValidationError({'lines': 'Au moins une ligne de reception est requise.'})
        seen = set()
        for line in lines:
            order_line = line['order_line']
            if order_line.order_id != order.id:
                raise serializers.ValidationError({'lines': 'Une ligne de reception ne correspond pas a cette commande.'})
            if order_line.id in seen:
                raise serializers.ValidationError({'lines': 'Une ligne de commande ne peut apparaitre qu une seule fois.'})
            seen.add(order_line.id)
            remaining = order_line.quantity_ordered - order_line.quantity_received
            if line['quantity_received'] > remaining:
                raise serializers.ValidationError({'lines': f'Quantite recue superieure au restant pour {order_line.product.name}.'})
        return attrs

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        request = self.context.get('request')
        audit_user = getattr(request, 'user', None)
        with transaction.atomic():
            reception = Reception.objects.create(**validated_data)
            for line_data in lines_data:
                ReceptionLine.objects.create(reception=reception, **line_data)
                order_line = line_data['order_line']
                quantity_received = line_data['quantity_received']

                order_line.quantity_received += quantity_received
                order_line.save(update_fields=['quantity_received'])

                product = order_line.product
                stock_before = product.current_stock
                product.current_stock += quantity_received
                product.save(update_fields=['current_stock', 'updated_at'])

                reference = reception.reference or reception.order.reference
                StockMovement.objects.create(
                    product=product,
                    type='entree',
                    quantity=quantity_received,
                    stock_before=stock_before,
                    stock_after=product.current_stock,
                    reference=reference,
                    reason=f"Reception {reception.reference or reception.id} - Commande {reception.order.reference}",
                    performed_by=reception.received_by,
                )
                create_audit_log(
                    audit_user,
                    'stock_update',
                    'Product',
                    product.id,
                    f"Stock augmente de {quantity_received} apres reception {reception.reference or reception.id}.",
                )

            order = reception.order
            if all(line.is_fully_received for line in order.order_lines.all()):
                order.status = 'recue'
            else:
                order.status = 'recue_partielle'
            order.save(update_fields=['status', 'updated_at'])
            create_audit_log(
                audit_user,
                'reception_creation',
                'Reception',
                reception.id,
                f"Reception creee pour la commande {order.reference}.",
            )
        return reception
