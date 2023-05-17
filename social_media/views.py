from django.db.models import QuerySet
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

import permissions
from social_media.models import Profile, Follow
from social_media.serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = permissions.IsOwnerOrReadOnly,

    def get_queryset(self) -> QuerySet:
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        nick_name = self.request.query_params.get("nick_name")
        sex = self.request.query_params.get("sex")

        queryset = self.queryset

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        if nick_name:
            queryset = queryset.filter(nick_name__icontains=nick_name)

        if sex:
            queryset = queryset.filter(sex__exact=sex)

        return queryset.distinct()

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)

    @action(methods=["GET", "DELETE", "PATCH"], detail=False, url_path="me")
    def me(self, request: Request) -> Response:
        profile = get_object_or_404(Profile, user=self.request.user)

        if request.method == "GET":
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "PATCH":
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        elif request.method == "DELETE":
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=True, url_path="follow")
    def follow(self, request: Request, pk=None) -> Response:
        profile_to_follow = self.get_object()
        follower = request.user
        if follower.following.filter(following=profile_to_follow).exists():
            return Response({"message": "You are already following this profile"}, status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(follower=follower, following=profile_to_follow)
        return Response({"message": "Now you now following this profile"}, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=True, url_path="unfollow")
    def unfollow(self, request: Request, pk=None) -> Response:
        profile_to_unfollow = self.get_object()
        follower = request.user
        if not follower.following.filter(following=profile_to_unfollow).exists():
            return Response({"message": "You are not follow this profile"}, status=status.HTTP_400_BAD_REQUEST)
        follow = follower.following.get(following=profile_to_unfollow)
        follow.delete()
        return Response({"message": "You have unfollowed this profile"})
