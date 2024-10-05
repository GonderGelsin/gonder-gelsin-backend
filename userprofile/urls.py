from django.urls import path

from .api import (CheckUserAPI, TestAPI, UserLanguageAPI, UserNotificationAPI,
                  UserProfileDetailAPI)

urlpatterns = [
    path("", UserProfileDetailAPI.as_view()),
    path("users/", TestAPI.as_view()),
    path("notification/preferences/", UserNotificationAPI.as_view()),
    path("language/", UserLanguageAPI.as_view()),
    path("check-user/", CheckUserAPI.as_view()),

]
