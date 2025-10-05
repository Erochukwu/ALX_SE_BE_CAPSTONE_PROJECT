from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from followers.models import Follow
from followers.serializers import FollowSerializer
from users.models import CustomerProfile, VendorProfile


class FollowViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing follows.
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned follows to the current customer.
        """
        user = self.request.user
        if hasattr(user, "customer_profile"):
            return Follow.objects.filter(customer=user.customer_profile)
        return Follow.objects.none()

    def perform_create(self, serializer):
        """
        Automatically set the customer as the current authenticated user.
        """
        serializer.save(customer=self.request.user.customer_profile)

    @action(detail=True, methods=["delete"], url_path="unfollow")
    def unfollow(self, request, pk=None):
        """
        Allows a customer to unfollow a vendor.
        """
        try:
            follow = Follow.objects.get(customer=request.user.customer_profile, vendor_id=pk)
            follow.delete()
            return Response({"detail": "Unfollowed successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response({"detail": "Follow relationship not found"}, status=status.HTTP_404_NOT_FOUND)
