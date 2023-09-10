from django.urls import path
from rest_framework import routers

from .views import (FileViewSet, LintFileViewSet, UserViewSet, login_api,
                    register_api)

router = routers.DefaultRouter()
router.register(r"file", FileViewSet, basename="file")
router.register(r"filecheck", LintFileViewSet)
router.register(r"user", UserViewSet, basename="user")

urlpatterns = [
    path("register/", register_api, name="register_api"),
    path("login/", login_api, name="login_api"),
] + router.urls
