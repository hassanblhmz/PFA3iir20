"""
Vues pour les demandes d'achat, commandes et réceptions
"""
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import PurchaseRequest, ValidationLog, PurchaseOrder, Reception, AuditLog
from .serializers import (
    PurchaseRequestSerializer, PurchaseRequestListSerializer,
    PurchaseOrderSerializer, PurchaseOrderListSerializer,
    ReceptionSerializer, ValidationLogSerializer
)
from users.permissions import IsValidateur, IsAdminOrAcheteur, IsMagasinier


def create_audit_log(user, action, entity, entity_id=None, description=''):
    """Create audit entries for sensitive workflow actions without blocking the response."""
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


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    """Gestion des demandes d'achat"""
    queryset = PurchaseRequest.objects.select_related('requested_by').prefetch_related('lines')
    serializer_class = PurchaseRequestSerializer
    search_fields = ['reference', 'title', 'department']
    filterset_fields = ['status', 'priority', 'requested_by']
    ordering_fields = ['created_at', 'needed_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseRequestListSerializer
        return PurchaseRequestSerializer

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user, department=self.request.user.department)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Soumettre une demande pour validation"""
        pr = self.get_object()
        if pr.status != 'brouillon':
            return Response({'error': 'Seul un brouillon peut être soumis.'}, status=400)
        if pr.requested_by != request.user and request.user.role != 'admin':
            return Response({'error': 'Non autorisé.'}, status=403)
        old_status = pr.status
        pr.status = 'soumis'
        pr.submitted_at = timezone.now()
        pr.save()
        ValidationLog.objects.create(
            request=pr, action='soumission', performed_by=request.user,
            old_status=old_status, new_status='soumis'
        )
        return Response({'message': 'Demande soumise avec succès.', 'status': pr.status})

    @action(detail=True, methods=['post'], permission_classes=[IsValidateur])
    def validate(self, request, pk=None):
        """Valider une demande d'achat"""
        pr = self.get_object()
        if pr.status not in ['soumis', 'en_validation']:
            return Response({'error': 'Cette demande ne peut pas être validée.'}, status=400)
        comment = request.data.get('comment', '')
        old_status = pr.status
        pr.status = 'valide'
        pr.save()
        ValidationLog.objects.create(
            request=pr, action='validation', performed_by=request.user,
            comment=comment, old_status=old_status, new_status='valide'
        )
        create_audit_log(
            request.user,
            'request_validation',
            'PurchaseRequest',
            pr.id,
            f"Demande {pr.reference} validee.",
        )
        return Response({'message': 'Demande validée.', 'status': pr.status})

    @action(detail=True, methods=['post'], permission_classes=[IsValidateur])
    def reject(self, request, pk=None):
        """Rejeter une demande d'achat"""
        pr = self.get_object()
        if pr.status not in ['soumis', 'en_validation']:
            return Response({'error': 'Cette demande ne peut pas être rejetée.'}, status=400)
        comment = request.data.get('comment', '')
        if not comment:
            return Response({'error': 'Un commentaire est requis pour le rejet.'}, status=400)
        old_status = pr.status
        pr.status = 'rejete'
        pr.save()
        ValidationLog.objects.create(
            request=pr, action='rejet', performed_by=request.user,
            comment=comment, old_status=old_status, new_status='rejete'
        )
        create_audit_log(
            request.user,
            'request_rejection',
            'PurchaseRequest',
            pr.id,
            f"Demande {pr.reference} rejetee.",
        )
        return Response({'message': 'Demande rejetée.', 'status': pr.status})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrAcheteur])
    def create_order(self, request, pk=None):
        """Générer un bon de commande depuis une demande validée"""
        pr = self.get_object()
        if pr.status != 'valide':
            return Response({'error': 'Seule une demande validée peut générer une commande.'}, status=400)
        if hasattr(pr, 'order'):
            return Response({'error': 'Un bon de commande existe déjà.'}, status=400)

        supplier_id = request.data.get('supplier_id')
        if not supplier_id:
            return Response({'error': 'Fournisseur requis.'}, status=400)

        from suppliers.models import Supplier
        from purchases.models import PurchaseOrder, PurchaseOrderLine
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        with transaction.atomic():
            order = PurchaseOrder.objects.create(
                purchase_request=pr,
                supplier=supplier,
                ordered_by=request.user,
                expected_date=request.data.get('expected_date'),
            )
            for line in pr.lines.all():
                PurchaseOrderLine.objects.create(
                    order=order,
                    product=line.product,
                    quantity_ordered=line.quantity,
                    unit_price=line.unit_price,
                )
            pr.status = 'commande'
            pr.save(update_fields=['status', 'updated_at'])
            create_audit_log(
                request.user,
                'order_creation',
                'PurchaseOrder',
                order.id,
                f"Commande {order.reference} creee depuis la demande {pr.reference}.",
            )
        serializer = PurchaseOrderSerializer(order)
        return Response(serializer.data, status=201)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """Gestion des bons de commande"""
    queryset = PurchaseOrder.objects.select_related('supplier', 'ordered_by').prefetch_related('order_lines')
    serializer_class = PurchaseOrderSerializer
    search_fields = ['reference', 'supplier__name']
    filterset_fields = ['status', 'supplier']
    ordering_fields = ['created_at', 'expected_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseOrderListSerializer
        return PurchaseOrderSerializer

    def perform_create(self, serializer):
        serializer.save(ordered_by=self.request.user)
        create_audit_log(
            self.request.user,
            'order_creation',
            'PurchaseOrder',
            serializer.instance.id,
            f"Commande {serializer.instance.reference} creee.",
        )

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Marquer la commande comme envoyée"""
        order = self.get_object()
        if order.status != 'brouillon':
            return Response({'error': 'Seul un brouillon peut être envoyé.'}, status=400)
        order.status = 'envoyee'
        order.sent_at = timezone.now()
        order.save()
        return Response({'message': 'Commande envoyée.', 'status': order.status})


class ReceptionViewSet(viewsets.ModelViewSet):
    """Gestion des réceptions"""
    queryset = Reception.objects.select_related('order', 'received_by')
    serializer_class = ReceptionSerializer
    filterset_fields = ['order']

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)


class DashboardView(viewsets.ViewSet):
    """Dashboard statistiques"""

    def list(self, request):
        from products.models import Product
        from django.db.models import Sum, Count, F

        # Statistiques demandes
        total_requests = PurchaseRequest.objects.count()
        pending_requests = PurchaseRequest.objects.filter(status__in=['soumis', 'en_validation']).count()
        validated_requests = PurchaseRequest.objects.filter(status='valide').count()
        rejected_requests = PurchaseRequest.objects.filter(status='rejete').count()

        # Statistiques commandes
        total_orders = PurchaseOrder.objects.count()
        pending_orders = PurchaseOrder.objects.filter(status__in=['envoyee', 'confirmee']).count()

        # Stock critique
        critical_products = Product.objects.filter(
            current_stock__lte=F('min_stock'), is_active=True
        ).count()

        # Dépenses totales (commandes reçues)
        total_spent = sum(
            order.total_amount
            for order in PurchaseOrder.objects.filter(status__in=['recue', 'cloturee'])
        )

        # Demandes récentes
        recent_requests = PurchaseRequest.objects.order_by('-created_at')[:5]
        recent_serializer = PurchaseRequestListSerializer(recent_requests, many=True)

        return Response({
            'requests': {
                'total': total_requests,
                'pending': pending_requests,
                'validated': validated_requests,
                'rejected': rejected_requests,
            },
            'orders': {
                'total': total_orders,
                'pending': pending_orders,
            },
            'stock': {
                'critical_count': critical_products,
            },
            'finance': {
                'total_spent': float(total_spent),
            },
            'recent_requests': recent_serializer.data,
        })
