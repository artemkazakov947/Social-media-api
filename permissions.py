from rest_framework.permissions import BasePermission, SAFE_METHODS

from social_media.models import Profile, Comment


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if isinstance(obj, Profile):
            return obj.user == request.user

        elif isinstance(obj, Comment):
            return obj.author == request.user
