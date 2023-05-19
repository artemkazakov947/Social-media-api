from django.conf import settings
from rest_framework import serializers

from social_media.models import Profile, Post


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "first_name",
            "last_name",
            "nick_name",
            "email",
            "sex",
            "bio",
            "registered",
            "image",
        )
        read_only_fields = ("registered",)


class ProfileFollowersSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "nick_name", "email", "image",)


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.profile", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "topic",
            "created",
            "updated",
        )


class PostDetailSerializer(PostListSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "topic",
            "created",
            "updated",
            "text",
            "image",
        )
