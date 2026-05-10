"""
Modèles pour les demandes d'achat et commandes
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
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('commande', 'Commandé'),
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
        verbose_name='Demandé par'
    )
    department = models.CharField(max_length=100, blank=True, verbose_name='Département')
    needed_date = models.DateField(null=True, blank=True, verbose_name='Date souhaitée')
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
        # Génération automatique de la référence
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
        verbose_name='Article'
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Quantité')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Prix unitaire estimé')
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
    performed_by = models.ForeignKey(User, on_delete=models.PROTECT)
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

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=80)
    entity = models.CharField(max_length=80)
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class PurchaseOrder(models.Model):
    """Bon de commande généré depuis une demande validée"""

    STATUS_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoyee', 'Envoyée'),
        ('confirmee', 'Confirmée'),
        ('recue_partielle', 'Reçue partiellement'),
        ('recue', 'Reçue totalement'),
        ('cloturee', 'Clôturée'),
        ('annulee', 'Annulée'),
    ]

    reference = models.CharField(max_length=30, unique=True, blank=True)
    purchase_request = models.OneToOneField(
        PurchaseRequest, on_delete=models.PROTECT,
        related_name='order', null=True, blank=True
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT,
        verbose_name='Fournisseur'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon')
    ordered_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='purchase_orders'
    )
    expected_date = models.DateField(null=True, blank=True, verbose_name='Livraison prévue')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

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


class PurchaseOrderLine(models.Model):
    """Ligne d'une commande"""

    order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE,
        related_name='order_lines'
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
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
    """Réception partielle ou totale d'une commande"""

    order = models.ForeignKey(
        PurchaseOrder, on_delete=models.PROTECT,
        related_name='receptions'
    )
    received_by = models.ForeignKey(User, on_delete=models.PROTECT)
    reference = models.CharField(max_length=50, blank=True, verbose_name='BL Fournisseur')
    notes = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Réception'
        ordering = ['-received_at']


class ReceptionLine(models.Model):
    """Ligne d'une réception"""

    reception = models.ForeignKey(
        Reception, on_delete=models.CASCADE,
        related_name='lines'
    )
    order_line = models.ForeignKey(PurchaseOrderLine, on_delete=models.PROTECT)
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(max_length=200, blank=True)
