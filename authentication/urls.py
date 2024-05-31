from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .api import (PasswordResetRequestAPI, TestListAPI, UserSignInAPI,
                  UserSignUpAPI)

urlpatterns = [
    path('register/', UserSignUpAPI.as_view()),
    path('login/', UserSignInAPI.as_view()),
    path('revoke-token/', TokenRefreshView.as_view()),
    path('reset-password/', PasswordResetRequestAPI.as_view()),
    path('test/', TestListAPI.as_view())

]
