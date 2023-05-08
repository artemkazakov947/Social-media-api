from django.urls import path

from user.views import CreateUserView, UpdateUserView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create-user"),
    path("me/", UpdateUserView.as_view(), name="update-user"),
]

app_name = "user"
