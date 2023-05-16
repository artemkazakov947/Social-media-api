from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, profile):

        if request.method in SAFE_METHODS:
            return True

        return profile.user == request.user
