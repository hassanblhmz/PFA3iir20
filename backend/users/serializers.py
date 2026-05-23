"""
Serializers pour les utilisateurs et l'authentification
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT token avec données utilisateur enrichies"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Ajouter des claims personnalisés au token
        token['role'] = user.role
        token['full_name'] = user.full_name
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Ajouter les infos utilisateur dans la réponse
        data['user'] = UserSerializer(self.user).data
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer complet pour un utilisateur"""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'role', 'supplier', 'phone', 'department', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'un utilisateur"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'role', 'supplier', 'phone', 'department', 'password', 'password_confirm'
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'un utilisateur"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'department', 'role', 'supplier', 'is_active']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour le changement de mot de passe"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
