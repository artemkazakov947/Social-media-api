# Generated by Django 4.2.1 on 2023-05-18 11:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("social_media", "0004_alter_post_options_post_updated_alter_post_pub_date"),
    ]

    operations = [
        migrations.RenameField(
            model_name="post",
            old_name="pub_date",
            new_name="created",
        ),
    ]
