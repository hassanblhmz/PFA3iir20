"""
Vues pour la gestion des utilisateurs
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import update_session_auth_hash

from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer,
    UserCreateSerializer, UserUpdateSerializer, ChangePasswordSerializer
)
from .permissions import IsAdmin


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vue de connexion JWT personnalisée"""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """CRUD complet pour les utilisateurs (admin uniquement)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ['email', 'first_name', 'last_name', 'department']
    filterset_fields = ['role', 'is_active']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdmin()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retourne le profil de l'utilisateur connecté"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Changement de mot de passe"""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get('old_password')):
                return Response(
                    {'old_password': 'Mot de passe incorrect.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'message': 'Mot de passe mis à jour avec succès.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """Inscription (accessible sans authentification)"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
