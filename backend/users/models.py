"""
Modèles utilisateurs avec gestion des rôles
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé avec rôles métier
    """
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('demandeur', 'Demandeur'),
        ('validateur', 'Validateur'),
        ('acheteur', 'Acheteur'),
        ('magasinier', 'Magasinier'),
        ('direction', 'Direction'),
        ('fournisseur', 'Fournisseur'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='demandeur')
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.SET_NULL,
        related_name='users',
        null=True,
        blank=True,
        verbose_name='Fournisseur lie',
    )
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
