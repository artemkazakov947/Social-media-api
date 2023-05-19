from django.db.models import QuerySet
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

import permissions
from social_media.models import Profile, Follow, Post
from social_media.serializers import (
    ProfileSerializer,
    ProfileFollowersSerializer,
    PostListSerializer,
    PostDetailSerializer
)
from user.serializers import UserSerializer


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

    @action(methods=["GET"], detail=False, url_path="me/list_followers")
    def list_followers(self, request: Request) -> Response:
        user_profile = request.user.profile
        followers = Follow.objects.filter(following=user_profile)
        followers_profile = [follower.follower.profile for follower in followers]
        serializer = ProfileFollowersSerializer(followers_profile, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, url_path="me/list_following")
    def list_following(self, request: Request) -> Response:
        user = request.user
        followings = Follow.objects.filter(follower=user)
        following_users = [following.following.user for following in followings]
        serializer = UserSerializer(following_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = permissions.IsOwnerOrReadOnly,

    def get_serializer_class(self):
        if self.action == 'my_posts':
            if self.request.method == 'GET':
                return PostListSerializer
            elif self.request.method == 'POST':
                return PostDetailSerializer

        serializer_classes = {
            "list": PostListSerializer,
            "create": PostDetailSerializer,
            "retrieve": PostDetailSerializer,
            "update": PostDetailSerializer,
            "partial_update": PostDetailSerializer,
        }
        return serializer_classes.get(self.action)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["GET", "POST"], url_path="my_posts", detail=False)
    def my_posts(self, request: Request) -> Response:
        if request.method == "GET":
            posts = Post.objects.filter(user=request.user)
            serializer = PostListSerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "POST":
            serializer = PostDetailSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET"], detail=False, url_path="following_posts")
    def following_posts(self, request: Request) -> Response:
        following_profiles = Profile.objects.filter(followers__follower=request.user)
        posts = Post.objects.filter(user__profile__in=following_profiles)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

