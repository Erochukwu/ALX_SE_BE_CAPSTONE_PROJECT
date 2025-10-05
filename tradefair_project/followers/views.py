"""
followers/views.py

API views for following and unfollowing vendors.
- Customers can follow/unfollow vendors.
- Vendors can view their followers.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Follow
from .serializers import FollowSerializer
from .permissions import IsVendor, IsCustomer


class FollowViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Follower model.
    """
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Dynamically assign permissions depending on action.
        """
        if self.action in ["create", "unfollow", "destroy"]:
            # Customers can follow or unfollow vendors
            return [IsCustomer()]
        elif self.action in ["list", "retrieve"]:
            # Authenticated users can list their own relationships
            return [permissions.IsAuthenticated()]
        elif self.action in ["my_followers"]:
            # Vendors only
            return [IsVendor()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user

        # Vendors: view their followers
        if hasattr(user, "vendor_profile"):
            return Follow.objects.filter(vendor__user=user)

        # Customers: view vendors they follow
        if hasattr(user, "customer_profile"):
            return Follow.objects.filter(customer__user=user)

        return Follow.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, "customer_profile"):
            raise PermissionDenied("Only customers can follow vendors.")

        serializer.save(customer=user.customer_profile)

    @action(detail=False, methods=["post"])
    def unfollow(self, request):
        """
        POST /api/followers/unfollow/
        Unfollow a vendor.
        """
        user = request.user
        vendor_id = request.data.get("vendor_id")

        if not vendor_id:
            return Response({"detail": "vendor_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not hasattr(user, "customer_profile"):
            raise PermissionDenied("Only customers can unfollow vendors.")

        deleted, _ = Follow.objects.filter(
            customer=user.customer_profile, vendor_id=vendor_id
        ).delete()

        if deleted:
            return Response({"detail": "Vendor unfollowed successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "You are not following this vendor."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def my_followers(self, request):
        """
        GET /api/followers/my_followers/
        Allows a vendor to view all their followers.
        """
        user = request.user

        if not hasattr(user, "vendor_profile"):
            raise PermissionDenied("Only vendors can view followers.")

        followers = Follow.objects.filter(vendor__user=user)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)