from rest_framework.routers import DefaultRouter
from social_media.views import ProfileViewSet

router = DefaultRouter()

router.register("profiles", ProfileViewSet)

urlpatterns = router.urls

app_name = "social_media"
