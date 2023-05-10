from django.conf import settings
from rest_framework import serializers

from social_media.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.SlugRelatedField(
        source=settings.AUTH_USER_MODEL, slug_field="email", many=False, read_only=False
    )

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
            "image"
        )
        read_only_fields = ("registered", )

