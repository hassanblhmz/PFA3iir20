"""
Modèles pour la gestion des articles et catégories
"""
from decimal import Decimal

from django.db import models
from suppliers.models import Supplier


class Category(models.Model):
    """Catégorie d'article"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Nom')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Article/produit avec gestion des seuils de stock"""

    UNIT_CHOICES = [
        ('pièce', 'Pièce'),
        ('kg', 'Kilogramme'),
        ('litre', 'Litre'),
        ('carton', 'Carton'),
        ('palette', 'Palette'),
        ('mètre', 'Mètre'),
        ('lot', 'Lot'),
    ]

    code = models.CharField(max_length=30, unique=True, verbose_name='Référence')
    name = models.CharField(max_length=200, verbose_name='Désignation')
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name='products', verbose_name='Catégorie'
    )
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pièce', verbose_name='Unité')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Prix unitaire')
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Stock actuel')
    min_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Seuil minimum')
    max_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Stock maximum')
    suppliers = models.ManyToManyField(
        Supplier, blank=True,
        related_name='products', verbose_name='Fournisseurs'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_critical(self):
        """Retourne True si le stock est en dessous du seuil minimum"""
        return self.current_stock <= self.min_stock

    @property
    def stock_status(self):
        if not self.is_active:
            return 'indisponible'
        if self.current_stock <= 0:
            return 'rupture'
        elif self.current_stock <= self.min_stock:
            return 'critique'
        elif self.current_stock <= self.min_stock * Decimal('1.5'):
            return 'faible'
        return 'normal'

    @property
    def stock_status_label(self):
        labels = {
            'indisponible': 'Indisponible',
            'rupture': 'Rupture',
            'critique': 'Critique',
            'faible': 'Faible',
            'normal': 'Normal',
        }
        return labels[self.stock_status]
