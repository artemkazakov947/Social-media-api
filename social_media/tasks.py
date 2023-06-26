from celery import shared_task
from django.contrib.auth import get_user_model

from social_media.models import Post


@shared_task
def schedule_post():
    admin = get_user_model().objects.get(email="admin@admin.com")
    text = "Time to donate to ZSU"
    Post.objects.create(topic="daily task", text=text, user=admin)
