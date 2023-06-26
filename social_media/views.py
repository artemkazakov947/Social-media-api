from django.db.models import QuerySet, Q
from django.utils.functional import cached_property
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

import permissions
from social_media.models import Profile, Follow, Post, Comment, Like
from social_media.serializers import (
    ProfileSerializer,
    ProfileFollowersSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
)
from user.serializers import UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all().select_related("user")
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsOwnerOrReadOnly,)

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="first_name",
                type={"type": "str"},
                description="Filter for first_name "
                "(ex ex ?first_name=artem will return all users with first_name artem or users first_name wich include 'artem')",
                required=False,
            ),
            OpenApiParameter(
                name="last_name",
                type={"type": "str"},
                description="Filter for last_name "
                "(ex ?last_name=kazakov will return all users with last_name kazakov or users last_name wich include 'kazakov')",
                required=False,
                allow_blank=True,
            ),
            OpenApiParameter(
                name="nick_name",
                description="Filter for nick_name "
                "(ex ?nick_name=hellford will return all users with nick_name hellford or users nick_name wich include 'hellford')",
                required=False,
                allow_blank=True,
            ),
            OpenApiParameter(
                name="sex",
                description="Filter for sex of user "
                "(ex ?last_name=Woman will return all users women)",
                required=False,
                allow_blank=True,
            ),
        ],
        description="Users are able to search for profiles by username or other criteria",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """User can update only their own profile"""
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """User can patch only their own profile"""
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """User can delete only their own profile"""
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)

    @action(methods=["GET", "DELETE", "PATCH"], detail=False, url_path="me")
    def me(self, request: Request) -> Response:
        """Users are able to retrieve their own profile"""
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
            return Response(
                {"message": "Profile was deleted"}, status=status.HTTP_204_NO_CONTENT
            )

    @extend_schema(
        description="Users are able to follow other profiles.",
        responses={
            status.HTTP_200_OK: "Now you now following this profile",
            status.HTTP_400_BAD_REQUEST: "You are already following this profile",
        },
    )
    @action(methods=["GET"], detail=True, url_path="follow")
    def follow(self, request: Request, pk=None) -> Response:
        profile_to_follow = self.get_object()
        follower = request.user
        if follower.following.filter(following=profile_to_follow).exists():
            return Response(
                {"message": "You are already following this profile"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Follow.objects.create(follower=follower, following=profile_to_follow)
        return Response(
            {"message": "Now you now following this profile"}, status=status.HTTP_200_OK
        )

    @extend_schema(
        description="Users are able to unfollow other profiles.",
        responses={
            status.HTTP_200_OK: "You have unfollowed this profile",
            status.HTTP_400_BAD_REQUEST: "You are not follow this profile",
        },
    )
    @action(methods=["GET"], detail=True, url_path="unfollow")
    def unfollow(self, request: Request, pk=None) -> Response:
        profile_to_unfollow = self.get_object()
        follower = request.user
        if not follower.following.filter(following=profile_to_unfollow).exists():
            return Response(
                {"message": "You are not follow this profile"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow = follower.following.get(following=profile_to_unfollow)
        follow.delete()
        return Response(
            {"message": "You have unfollowed this profile"}, status=status.HTTP_200_OK
        )

    @extend_schema(
        description="List the profiles being followed by the authenticated user",
        responses={status.HTTP_200_OK: ProfileFollowersSerializer},
    )
    @action(methods=["GET"], detail=False, url_path="me/list_following")
    def list_following(self, request: Request) -> Response:
        """Users are able to view the list of profiles they are following"""
        user_profile = request.user.profile
        followers = Follow.objects.filter(following=user_profile).select_related(
            "follower"
        )
        followers_profile = Profile.objects.filter(user__following__in=followers)
        serializer = ProfileFollowersSerializer(followers_profile, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={status.HTTP_200_OK: UserSerializer})
    @action(methods=["GET"], detail=False, url_path="me/list_followers")
    def list_followers(self, request: Request) -> Response:
        """Users are able to view the list of users following them"""
        user = request.user
        followings = Follow.objects.filter(follower=user)
        following_users = [following.following.user for following in followings]
        serializer = UserSerializer(following_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related("user__profile")
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "my_posts":
            if self.request.method == "GET":
                return PostListSerializer
            elif self.request.method == "POST":
                return PostDetailSerializer

        serializer_classes = {
            "list": PostListSerializer,
            "create": PostDetailSerializer,
            "retrieve": PostDetailSerializer,
            "update": PostDetailSerializer,
            "partial_update": PostDetailSerializer,
        }
        return serializer_classes.get(self.action)

    def get_queryset(self):
        queryset = self.queryset
        hashtag = self.request.query_params.get("hashtag")

        if hashtag:
            queryset = queryset.filter(
                Q(text__icontains=f"#{hashtag}") | Q(topic__icontains=f"#{hashtag}")
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["GET", "POST"], url_path="my_posts", detail=False)
    def my_posts(self, request: Request) -> Response:
        """Users are able to retrieve a list of their own posts and create new one"""
        if request.method == "GET":
            posts = Post.objects.filter(user=request.user).select_related(
                "user__profile"
            )
            serializer = PostListSerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "POST":
            serializer = PostDetailSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Users are able to retrieve posts of users they are following.",
        responses={status.HTTP_200_OK: PostListSerializer}
    )
    @action(methods=["GET"], detail=False, url_path="following_posts")
    def following_posts(self, request: Request) -> Response:
        following_profiles = Profile.objects.filter(followers__follower=request.user)
        posts = Post.objects.filter(user__profile__in=following_profiles)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Users are able to like and unlike posts.",
        responses={status.HTTP_200_OK: PostDetailSerializer}
    )
    @action(methods=["GET"], detail=True, url_path="like_unlike")
    def like_unlike(self, request: Request, pk=None) -> Response:
        post = get_object_or_404(Post, pk=pk)
        is_liked = post.likes.filter(user=request.user)
        serializer = PostDetailSerializer(post)
        if not is_liked:
            Like.objects.create(post=post, user=request.user)
        else:
            like = Like.objects.get(post=post, user=request.user)
            like.delete()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Users are able to view the list of posts they have liked.",
        responses={status.HTTP_200_OK: PostListSerializer}
    )
    @action(methods=["GET"], detail=False, url_path="liked_posts")
    def liked_posts(self, request):
        likes = Like.objects.filter(user=request.user).select_related("post")
        posts_id = [like.post.id for like in likes]
        posts = Post.objects.filter(id__in=posts_id)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="hashtag",
                type={"type": "str"},
                description="Filter for posts by hashtag "
                "(ex ?hashtag=hashtag will return all posts with 'hashtag' word in topic or in text)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related("author", "post")
    serializer_class = CommentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsOwnerOrReadOnly,)

    @cached_property
    def get_post(self) -> Post:
        post_id = self.kwargs.get("post_pk")
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("A post with given id does not exist")
        return post

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(author=self.request.user, post=self.get_post)

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(post=self.get_post)
