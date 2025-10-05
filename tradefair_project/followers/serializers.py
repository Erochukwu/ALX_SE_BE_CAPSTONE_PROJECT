from rest_framework import serializers
from followers.models import Follow

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ["id", "vendor"]
        read_only_fields = ["id"]
