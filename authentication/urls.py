from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .api import UserSignInAPI, UserSignUpAPI

urlpatterns = [
    path('register/', UserSignUpAPI.as_view()),
    path('login/', UserSignInAPI.as_view()),
    path('revoke-token/', TokenRefreshView.as_view()),
]
