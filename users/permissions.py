from rest_framework.permissions import BasePermission


class IsAdminOrSuperAdmin(BasePermission):
    """Allows access only to admin or super_admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_user


class IsSuperAdmin(BasePermission):
    """Allows access only to super_admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner can access their own record; admins can access any."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_user:
            return True
        # The object must have a 'user' FK or be the user itself
        owner = getattr(obj, 'user', obj)
        return owner == request.user
