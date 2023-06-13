import os.path
import uuid

from django.conf import settings
from django.db import models
from user.models import User


def profile_image_file_path(instance, filename: str):
    _, extension = os.path.splitext(filename)

    file = f"{instance.user.email}-{uuid.uuid4()}.{extension}"

    return os.path.join("uploads/profiles/", file)


def post_image_file_path(instance, filename: str):
    _, extension = os.path.splitext(filename)

    file = f"{instance.user.email}-{uuid.uuid4()}.{extension}"

    return os.path.join("uploads/posts/", file)


class Profile(models.Model):
    class SexChoices(models.TextChoices):
        MAN = "Man"
        WOMAN = "Woman"
        ANOTHER = "Another"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
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
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        unique_together = ("follower", "following")


class Post(models.Model):
    topic = models.CharField(max_length=255)
    text = models.TextField()
    image = models.ImageField(null=True, upload_to=post_image_file_path)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated"]

    def __str__(self):
        return f"Author: {self.user}, date: {self.created}"

    @property
    def get_likes(self) -> int:
        return self.likes.count()

    @property
    def get_likers(self) -> list:
        likes = Like.objects.filter(post=self)
        return [like.user.email for like in likes]


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")


class Comment(models.Model):
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Comment by {self.author} to post id: {self.post.id}"
