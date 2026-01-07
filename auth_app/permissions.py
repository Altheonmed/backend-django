from rest_framework import permissions
from .models import Doctor, Workplace

class IsDoctor(permissions.BasePermission):
    """
    Permission personnalisée pour autoriser uniquement les médecins à accéder à une vue.
    """
    def has_permission(self, request, view):
        # Vérifie si l'utilisateur est authentifié et s'il a un profil de docteur
        return request.user.is_authenticated and hasattr(request.user, 'doctor')

class IsCreator(permissions.BasePermission):
    """
    Permission personnalisée pour autoriser uniquement le créateur d'un objet.
    S'applique aux actions 'retrieve', 'update', 'destroy'.
    """
    def has_object_permission(self, request, view, obj):
        # Les permissions de lecture (GET, HEAD, OPTIONS) sont toujours autorisées
        if request.method in permissions.SAFE_METHODS:
            return True

        # S'il s'agit d'un objet Workplace, vérifie si l'utilisateur est le créateur
        if isinstance(obj, Workplace):
            return obj.creator and obj.creator.user == request.user
        
        # Pour les autres cas, la permission est refusée
        return False