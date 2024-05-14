from django.urls import path

from .api import UserProfileDetailAPI, TestAPI

urlpatterns = [
    path("", UserProfileDetailAPI.as_view()),
    path("users/", TestAPI.as_view()),

]
