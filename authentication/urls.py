from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .api import (CompleteProfileAPI, PasswordResetRequestAPI, UserDeviceAPI,
                  UserSignInAPI, UserSignUpAPI, google_sign_in)

urlpatterns = [
    path('register/', UserSignUpAPI.as_view()),
    path('login/', UserSignInAPI.as_view()),
    path('revoke-token/', TokenRefreshView.as_view()),
    path('reset-password/', PasswordResetRequestAPI.as_view()),
    path('device-token/', UserDeviceAPI.as_view()),
    path('google/login/', google_sign_in),
    path('google/complete-profile/', CompleteProfileAPI.as_view()),

]
