from rest_framework.routers import DefaultRouter
from followers.views import FollowViewSet

router = DefaultRouter()
router.register(r'followers', FollowViewSet, basename='follow')

urlpatterns = router.urls
