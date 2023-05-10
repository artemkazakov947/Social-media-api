# Generated by Django 4.2.1 on 2023-05-10 08:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import social_media.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("nick_name", models.CharField(max_length=255)),
                (
                    "sex",
                    models.CharField(
                        choices=[
                            ("Man", "Man"),
                            ("Woman", "Woman"),
                            ("Another", "Another"),
                        ],
                        default="Another",
                        max_length=7,
                    ),
                ),
                ("registered", models.DateField(auto_now_add=True)),
                ("bio", models.TextField()),
                (
                    "image",
                    models.ImageField(
                        null=True, upload_to=social_media.models.profile_image_file_path
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("last_name", "nick_name")},
            },
        ),
    ]
