from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from followers.models import Follow
from followers.serializers import FollowSerializer
from users.models import CustomerProfile, VendorProfile
from rest_framework.permissions import BasePermission

class IsCustomer(BasePermission):
    """
    Custom permission to ensure only users with a CustomerProfile can perform actions.
    """
    def has_permission(self, request, view):
        """
        Check if the user has a CustomerProfile.

        Args:
            request: The HTTP request object.
            view: The view being accessed.

        Returns:
            bool: True if the user has a CustomerProfile, False otherwise.
        """
        return hasattr(request.user, 'customer_profile')

class FollowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing follow relationships between customers and vendors.

    Provides endpoints to list, create, and delete follow relationships, with a custom
    action to unfollow vendors. Only authenticated customers can perform actions.
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        """
        Restrict the queryset to follows associated with the authenticated customer's profile.

        Returns:
            QuerySet: Follow objects filtered by the current user's CustomerProfile,
                      or an empty queryset if the user is not a customer.
        """
        user = self.request.user
        if hasattr(user, "customer_profile"):
            return Follow.objects.filter(customer=user.customer_profile)
        return Follow.objects.none()

    def perform_create(self, serializer):
        """
        Create a new follow relationship, automatically setting the customer to the authenticated user.

        Args:
            serializer: The FollowSerializer instance with validated data.
        """
        serializer.save(customer=self.request.user.customer_profile)

    @action(detail=True, methods=["delete"], url_path="unfollow")
    def unfollow(self, request, pk=None):
        """
        Allow a customer to unfollow a vendor by deleting the follow relationship.

        Args:
            request: The HTTP request object.
            pk: The primary key of the vendor to unfollow.

        Returns:
            Response: HTTP 204 if successful, HTTP 404 if the follow relationship does not exist.
        """
        try:
            follow = Follow.objects.get(customer=request.user.customer_profile, vendor_id=pk)
            follow.delete()
            return Response({"detail": "Unfollowed successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response({"detail": "Follow relationship not found"}, status=status.HTTP_404_NOT_FOUND)