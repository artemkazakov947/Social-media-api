from django.urls import path

from user.views import CreateUserView, UpdateUserView, CreateTokenView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create-user"),
    path("me/", UpdateUserView.as_view(), name="update-user"),
    path("login/", CreateTokenView.as_view())
]

app_name = "user"
