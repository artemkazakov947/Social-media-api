import os.path
import uuid

from django.conf import settings
from django.db import models


def profile_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)

    file = f"{instance.user.email}-{uuid.uuid4()}.{extension}"

    return os.path.join("uploads/profiles/", file)


class Profile(models.Model):
    class SexChoices(models.TextChoices):
        MAN = "Man"
        WOMAN = "Woman"
        ANOTHER = "Another"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user"
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    nick_name = models.CharField(max_length=255)
    sex = models.CharField(
        max_length=7, choices=SexChoices.choices, default=SexChoices.ANOTHER
    )
    registered = models.DateField(auto_now_add=True)
    bio = models.TextField()
    image = models.ImageField(null=True, upload_to=profile_image_file_path)

    class Meta:
        unique_together = (
            "last_name",
            "nick_name",
        )

    def __str__(self):
        return f"{self.first_name} {self.nick_name} {self.last_name}"


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ("follower", "following")
