from django.contrib import admin

from social_media.models import Profile, Post, Follow, Comment

admin.site.register(Profile)
admin.site.register(Follow)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["id", "topic", "user", "created", "updated"]
    readonly_fields = list_display
    list_filter = ("user", "topic")
    search_fields = ("topic",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "post", "author", "created", "updated"]
    readonly_fields = list_display
    list_filter = ("author", "post")
    search_fields = ("post",)
