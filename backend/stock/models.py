"""
Modèle pour les mouvements de stock
"""
from django.db import models
from products.models import Product
from users.models import User


class StockMovement(models.Model):
    """Traçabilité de tous les mouvements de stock"""

    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('ajustement', 'Ajustement'),
        ('transfert', 'Transfert'),
        ('retour', 'Retour'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT,
        related_name='movements', verbose_name='Article'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Quantité')
    stock_before = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Stock avant')
    stock_after = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Stock après')
    reference = models.CharField(max_length=50, blank=True, verbose_name='Référence')
    reason = models.CharField(max_length=200, blank=True, verbose_name='Motif')
    performed_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Effectué par')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mouvement de stock'
        verbose_name_plural = 'Mouvements de stock'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} - {self.product.name} ({self.quantity})"
