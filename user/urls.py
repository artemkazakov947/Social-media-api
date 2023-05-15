from django.urls import path

from user.views import CreateUserView, UpdateUserView, CreateTokenView, LogoutUserView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create-user"),
    path("me/", UpdateUserView.as_view(), name="update-user"),
    path("login/", CreateTokenView.as_view()),
    path("logout/", LogoutUserView.as_view(), name="logout"),
]

app_name = "user"
