from rest_framework import permissions

class IsVendor(permissions.BasePermission):
    """
    Allows access only to vendor users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "vendorprofile")


class IsCustomer(permissions.BasePermission):
    """
    Allows access only to customer users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "customerprofile")
