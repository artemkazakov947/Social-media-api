from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from social_media.views import ProfileViewSet, PostViewSet, CommentViewSet

router = DefaultRouter()

router.register("profiles", ProfileViewSet)
router.register("posts", PostViewSet)

comment_router = routers.NestedSimpleRouter(
    router,
    r"posts",
    lookup="post"
)

comment_router.register(
    r"comments",
    CommentViewSet,
    basename="post-comment"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(comment_router.urls))
]

app_name = "social_media"
