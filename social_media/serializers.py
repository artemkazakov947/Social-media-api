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
    author = serializers.SlugRelatedField(
        source=settings.AUTH_USER_MODEL, slug_field="email", many=False, read_only=True
    )
    created = serializers.DateTimeField(source="post.pub_date", read_only=True)

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
        fields = (
            "id",
            "author",
            "topic",
            "created",
            "updated",
            "text",
            "image",
        )


