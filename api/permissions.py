from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """Allows only admin users to perform certain actions."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsChefOrAdmin(BasePermission):
    """Allows only chefs and admins to create/edit recipes."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'chef']


class IsOwnerOrReadOnly(BasePermission):
    """Allows recipe owners to edit their own recipes, others can only view."""
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:  # Allow read-only requests
            return True
        return obj.author == request.user or request.user.role == 'admin'
