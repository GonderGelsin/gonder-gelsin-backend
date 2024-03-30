from django.urls import path

from authentication.api import CustomUserAPI

from .api import UserSignInAPI, UserSignUpAPI, UserTokenTestAPI

urlpatterns = [
    path('', CustomUserAPI.as_view()),
    path('signup/', UserSignUpAPI.as_view()),
    path('login/', UserSignInAPI.as_view()),
    path('test_token/', UserTokenTestAPI.as_view()),
]
