"""
ModÃ¨les pour les demandes d'achat et commandes
"""
from django.db import models
from django.utils import timezone
from users.models import User
from suppliers.models import Supplier
from products.models import Product


class PurchaseRequest(models.Model):
    """Demande d'achat soumise par un demandeur"""

    STATUS_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('soumis', 'Soumis'),
        ('en_validation', 'En validation'),
        ('valide', 'ValidÃ©'),
        ('rejete', 'RejetÃ©'),
        ('commande', 'CommandÃ©'),
    ]

    reference = models.CharField(max_length=30, unique=True, blank=True)
    title = models.CharField(max_length=200, verbose_name='Objet')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon')
    priority = models.CharField(
        max_length=10,
        choices=[('normale', 'Normale'), ('urgente', 'Urgente'), ('critique', 'Critique')],
        default='normale'
    )
    requested_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='purchase_requests',
        verbose_name='DemandÃ© par'
    )
    department = models.CharField(max_length=100, blank=True, verbose_name='DÃ©partement')
    needed_date = models.DateField(null=True, blank=True, verbose_name='Date souhaitÃ©e')
    notes = models.TextField(blank=True, verbose_name='Remarques')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Demande d\'achat'
        verbose_name_plural = 'Demandes d\'achat'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def save(self, *args, **kwargs):
        # GÃ©nÃ©ration automatique de la rÃ©fÃ©rence
        if not self.reference:
            year = timezone.now().year
            count = PurchaseRequest.objects.filter(
                created_at__year=year
            ).count() + 1
            self.reference = f"DA-{year}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return sum(line.total_price for line in self.lines.all())


class PurchaseRequestLine(models.Model):
    """Ligne d'une demande d'achat"""

    request = models.ForeignKey(
        PurchaseRequest, on_delete=models.CASCADE,
        related_name='lines', verbose_name='Demande'
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT,
        related_name='request_lines',
        verbose_name='Article'
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='QuantitÃ©')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Prix unitaire estimÃ©')
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Ligne de demande'

    @property
    def total_price(self):
        return self.quantity * self.unit_price


class ValidationLog(models.Model):
    """Journal d'audit pour les validations/rejets"""

    ACTION_CHOICES = [
        ('soumission', 'Soumission'),
        ('validation', 'Validation'),
        ('rejet', 'Rejet'),
        ('annulation', 'Annulation'),
        ('modification', 'Modification'),
    ]

    request = models.ForeignKey(
        PurchaseRequest, on_delete=models.CASCADE,
        related_name='logs', verbose_name='Demande'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='validation_logs')
    comment = models.TextField(blank=True, verbose_name='Commentaire')
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de validation'
        ordering = ['-created_at']


class SupplierConsultation(models.Model):
    """Consultation envoyee a plusieurs fournisseurs pour comparer les devis"""

    STATUS_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoyee', 'Envoyee'),
        ('analyse', 'Analyse'),
        ('attribuee', 'Attribuee'),
        ('annulee', 'Annulee'),
    ]

    reference = models.CharField(max_length=30, unique=True, blank=True)
    purchase_request = models.ForeignKey(
        PurchaseRequest, on_delete=models.SET_NULL,
        related_name='consultations', null=True, blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    suppliers = models.ManyToManyField(Supplier, related_name='consultations', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='consultations')
    selected_quote = models.OneToOneField(
        'SupplierQuote', on_delete=models.SET_NULL,
        related_name='selected_for', null=True, blank=True
    )
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Consultation fournisseur'
        verbose_name_plural = 'Consultations fournisseurs'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reference:
            year = timezone.now().year
            count = SupplierConsultation.objects.filter(created_at__year=year).count() + 1
            self.reference = f"CF-{year}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def best_quote(self):
        return self.quotes.order_by('total_amount', 'delivery_days').first()

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.selected_quote_id and self.selected_quote.consultation_id != self.id:
            raise ValidationError('Le devis retenu doit appartenir a cette consultation.')


class SupplierQuote(models.Model):
    """Devis recu dans le cadre d'une consultation fournisseur"""

    consultation = models.ForeignKey(
        SupplierConsultation, on_delete=models.CASCADE,
        related_name='quotes'
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='quotes')
    reference = models.CharField(max_length=50, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_days = models.PositiveIntegerField(default=0)
    availability = models.CharField(max_length=120, blank=True)
    quality_score = models.PositiveSmallIntegerField(default=3)
    notes = models.TextField(blank=True)
    is_selected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Devis fournisseur'
        verbose_name_plural = 'Devis fournisseurs'
        ordering = ['total_amount', 'delivery_days']

    @property
    def score(self):
        price_part = max(0, 100000 - float(self.total_amount)) / 1000
        delay_part = max(0, 30 - self.delivery_days) * 2
        return round(price_part + delay_part + (self.quality_score * 10), 2)

    def __str__(self):
        return f"{self.supplier.name} - {self.total_amount}"


class SupplierRequestConversation(models.Model):
    """Discussion entre un fournisseur et le demandeur pour une ligne de demande"""

    TRIGGER_CHOICES = [
        ('demande', 'Demande fournisseur'),
        ('critique', 'Stock critique'),
        ('rupture', 'Rupture de stock'),
        ('indisponible', 'Article indisponible'),
    ]

    STATUS_CHOICES = [
        ('ouverte', 'Ouverte'),
        ('en_cours', 'En cours'),
        ('cloturee', 'Cloturee'),
    ]

    purchase_request = models.ForeignKey(
        PurchaseRequest, on_delete=models.CASCADE,
        related_name='supplier_conversations', verbose_name='Demande'
    )
    request_line = models.ForeignKey(
        PurchaseRequestLine, on_delete=models.CASCADE,
        related_name='supplier_conversations', verbose_name='Ligne de demande'
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT,
        related_name='request_conversations', verbose_name='Fournisseur'
    )
    demandeur = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='supplier_conversations', verbose_name='Demandeur'
    )
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ouverte')
    subject = models.CharField(max_length=200, blank=True, verbose_name='Objet')
    opened_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Conversation fournisseur'
        verbose_name_plural = 'Conversations fournisseurs'
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['request_line', 'supplier'],
                condition=models.Q(status__in=['ouverte', 'en_cours']),
                name='unique_open_supplier_conversation_per_line',
            )
        ]

    @staticmethod
    def trigger_for_product(product):
        if not product.is_active:
            return 'indisponible'
        if product.stock_status == 'rupture':
            return 'rupture'
        if product.stock_status == 'critique':
            return 'critique'
        return 'demande'

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.request_line_id and self.purchase_request_id != self.request_line.request_id:
            raise ValidationError('La ligne doit appartenir a la demande selectionnee.')

        product = self.request_line.product if self.request_line_id else None
        if not product:
            return

        expected_trigger = self.trigger_for_product(product)
        if not self.trigger:
            self.trigger = expected_trigger
        elif self.trigger != expected_trigger:
            raise ValidationError(
                f"Le declencheur doit etre '{expected_trigger}' pour cet article."
            )

    def save(self, *args, **kwargs):
        if not self.demandeur_id and self.purchase_request_id:
            self.demandeur = self.purchase_request.requested_by
        if not self.trigger and self.request_line_id:
            self.trigger = self.trigger_for_product(self.request_line.product)
        if not self.subject and self.request_line_id:
            self.subject = f"{self.request_line.product.name} - {self.get_trigger_display()}"
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def product(self):
        return self.request_line.product

    def __str__(self):
        return f"{self.supplier.name} / {self.purchase_request.reference} - {self.get_trigger_display()}"


class SupplierRequestMessage(models.Model):
    """Message dans une conversation entre fournisseur et demandeur"""

    SENDER_CHOICES = [
        ('demandeur', 'Demandeur'),
        ('fournisseur', 'Fournisseur'),
    ]

    conversation = models.ForeignKey(
        SupplierRequestConversation, on_delete=models.CASCADE,
        related_name='messages'
    )
    sender_type = models.CharField(max_length=20, choices=SENDER_CHOICES)
    sender_user = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='supplier_messages', null=True, blank=True
    )
    sender_supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT,
        related_name='sent_messages', null=True, blank=True
    )
    body = models.TextField(verbose_name='Message')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Message fournisseur'
        verbose_name_plural = 'Messages fournisseurs'
        ordering = ['created_at']

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.body or not self.body.strip():
            raise ValidationError('Le message ne peut pas etre vide.')
        if self.conversation_id and self.conversation.status == 'cloturee':
            raise ValidationError('Impossible de repondre a une conversation cloturee.')
        if self.sender_type == 'demandeur' and not self.sender_user_id:
            raise ValidationError('Un message demandeur doit etre lie a un utilisateur.')
        if self.sender_type == 'fournisseur' and not self.sender_supplier_id:
            raise ValidationError('Un message fournisseur doit etre lie a un fournisseur.')
        if self.sender_type == 'demandeur' and self.sender_supplier_id:
            raise ValidationError('Un message demandeur ne doit pas etre lie a un fournisseur.')
        if self.sender_type == 'fournisseur' and self.sender_user_id:
            raise ValidationError('Un message fournisseur ne doit pas etre lie a un utilisateur.')
        if self.conversation_id and self.sender_type == 'demandeur' and self.sender_user_id != self.conversation.demandeur_id:
            raise ValidationError('Seul le demandeur de la conversation peut envoyer ce message.')
        if self.conversation_id and self.sender_type == 'fournisseur' and self.sender_supplier_id != self.conversation.supplier_id:
            raise ValidationError('Seul le fournisseur de la conversation peut envoyer ce message.')

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.conversation_id and self.conversation.status == 'ouverte':
            self.conversation.status = 'en_cours'
            self.conversation.save(update_fields=['status', 'updated_at'])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_sender_type_display()} - {self.created_at:%Y-%m-%d %H:%M}"


class Notification(models.Model):
    """Notification simple affichee dans l'application"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=160)
    message = models.TextField(blank=True)
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class AuditLog(models.Model):
    """Journal d'audit transverse pour les actions sensibles"""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='audit_logs', null=True, blank=True)
    action = models.CharField(max_length=80)
    entity = models.CharField(max_length=80)
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class PurchaseOrder(models.Model):
    """Bon de commande gÃ©nÃ©rÃ© depuis une demande validÃ©e"""

    STATUS_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoyee', 'EnvoyÃ©e'),
        ('confirmee', 'ConfirmÃ©e'),
        ('expediee', 'Expediee'),
        ('recue_partielle', 'ReÃ§ue partiellement'),
        ('recue', 'ReÃ§ue totalement'),
        ('cloturee', 'ClÃ´turÃ©e'),
        ('annulee', 'AnnulÃ©e'),
    ]

    SUPPLIER_RESPONSE_CHOICES = [
        ('en_attente', 'En attente fournisseur'),
        ('devis_envoye', 'Devis envoye'),
        ('confirmee', 'Confirmee par fournisseur'),
        ('refusee', 'Refusee par fournisseur'),
        ('preparation', 'En preparation'),
        ('expediee', 'Expediee'),
        ('livree', 'Livree'),
    ]

    reference = models.CharField(max_length=30, unique=True, blank=True)
    purchase_request = models.OneToOneField(
        PurchaseRequest, on_delete=models.PROTECT,
        related_name='order', null=True, blank=True
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT,
        related_name='purchase_orders',
        verbose_name='Fournisseur'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon')
    ordered_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='purchase_orders'
    )
    expected_date = models.DateField(null=True, blank=True, verbose_name='Livraison prÃ©vue')
    notes = models.TextField(blank=True)
    supplier_response_status = models.CharField(
        max_length=20,
        choices=SUPPLIER_RESPONSE_CHOICES,
        default='en_attente',
        verbose_name='Statut fournisseur',
    )
    supplier_quote_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Montant devis fournisseur',
    )
    supplier_delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date livraison proposee',
    )
    supplier_document_reference = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='Reference devis/facture/BL',
    )
    supplier_note = models.TextField(blank=True, verbose_name='Note fournisseur')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    supplier_responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            year = timezone.now().year
            count = PurchaseOrder.objects.filter(
                created_at__year=year
            ).count() + 1
            self.reference = f"BC-{year}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return sum(line.total_price for line in self.order_lines.all())

    @property
    def effective_delivery_date(self):
        return self.supplier_delivery_date or self.expected_date


class PurchaseOrderLine(models.Model):
    """Ligne d'une commande"""

    order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE,
        related_name='order_lines'
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_lines')
    quantity_ordered = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Ligne de commande'

    @property
    def total_price(self):
        return self.quantity_ordered * self.unit_price

    @property
    def is_fully_received(self):
        return self.quantity_received >= self.quantity_ordered


class Reception(models.Model):
    """RÃ©ception partielle ou totale d'une commande"""

    order = models.ForeignKey(
        PurchaseOrder, on_delete=models.PROTECT,
        related_name='receptions'
    )
    received_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='receptions')
    reference = models.CharField(max_length=50, blank=True, verbose_name='BL Fournisseur')
    notes = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'RÃ©ception'
        ordering = ['-received_at']


class ReceptionLine(models.Model):
    """Ligne d'une rÃ©ception"""

    reception = models.ForeignKey(
        Reception, on_delete=models.CASCADE,
        related_name='lines'
    )
    order_line = models.ForeignKey(PurchaseOrderLine, on_delete=models.PROTECT, related_name='reception_lines')
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(max_length=200, blank=True)


