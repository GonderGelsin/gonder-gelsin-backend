from django.urls import path

from .api import TestAPI, UserNotificationAPI, UserProfileDetailAPI

urlpatterns = [
    path("", UserProfileDetailAPI.as_view()),
    path("users/", TestAPI.as_view()),
    path("notification/preferences/", UserNotificationAPI.as_view()),


]
