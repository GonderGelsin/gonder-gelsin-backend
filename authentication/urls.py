from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .api import UserSignUpAPI

urlpatterns = [
    path('signup/', UserSignUpAPI.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('revoke-token/', TokenRefreshView.as_view()),
]
