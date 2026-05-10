"""
Modèles pour la gestion des fournisseurs
"""
from django.db import models


class Supplier(models.Model):
    """Fournisseur avec toutes ses informations de contact et commerciales"""

    STATUS_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('suspendu', 'Suspendu'),
    ]

    name = models.CharField(max_length=200, verbose_name='Raison sociale')
    code = models.CharField(max_length=20, unique=True, verbose_name='Code fournisseur')
    contact_name = models.CharField(max_length=100, blank=True, verbose_name='Contact')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True, verbose_name='Adresse')
    city = models.CharField(max_length=100, blank=True, verbose_name='Ville')
    country = models.CharField(max_length=100, default='Maroc', verbose_name='Pays')
    ice = models.CharField(max_length=15, blank=True, verbose_name='ICE')  # Identifiant fiscal Maroc
    payment_terms = models.IntegerField(default=30, verbose_name='Délai paiement (jours)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='actif')
    notes = models.TextField(blank=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"
