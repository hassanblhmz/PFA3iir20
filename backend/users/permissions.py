"""
Permissions basées sur les rôles (RBAC)
"""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Seuls les administrateurs"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrAcheteur(BasePermission):
    """Admin ou Acheteur"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'acheteur']


class IsValidateur(BasePermission):
    """Admin ou Validateur"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'validateur']


class IsMagasinier(BasePermission):
    """Admin ou Magasinier"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'magasinier']


class IsDirection(BasePermission):
    """Admin ou Direction"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'direction']


class IsAdminOrReadOnly(BasePermission):
    """Admin en écriture, tout le monde en lecture"""
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in ['admin', 'acheteur']
