from rest_framework import serializers

from social_media.models import Profile, Post, Comment


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
        fields = (
            "first_name",
            "last_name",
            "nick_name",
            "email",
            "image",
        )


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.profile", read_only=True)
    likes = serializers.IntegerField(source="get_likes")

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "topic",
            "created",
            "updated",
            "likes",
        )


class PostDetailSerializer(PostListSerializer):
    liked_by = serializers.ReadOnlyField(source="get_likers")

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
            "liked_by"
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "post",
            "author",
            "created",
            "updated",
        )
        read_only_fields = ("author", "post")
