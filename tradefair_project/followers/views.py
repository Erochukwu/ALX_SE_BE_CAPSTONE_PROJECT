"""
API views for the followers app in the TradeFair project.

Handles follow and unfollow actions for customers and vendors.
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Follow
from .serializers import FollowSerializer
from users.models import CustomerProfile

class FollowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing follow relationships.

    Allows customers to follow/unfollow vendors and list their follows.
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return follows for the authenticated customer."""
        if hasattr(self.request.user, 'customer_profile'):
            return Follow.objects.filter(customer=self.request.user)
        return Follow.objects.none()

    def create(self, request, *args, **kwargs):
        """Allow customers to follow a vendor."""
        if not hasattr(request.user, 'customer_profile'):
            return Response(
                {"error": "Only customers can follow vendors"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Allow customers to unfollow a vendor."""
        if not hasattr(request.user, 'customer_profile'):
            return Response(
                {"error": "Only customers can unfollow vendors"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)