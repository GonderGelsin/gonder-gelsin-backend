from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .api import TransactionAPI, TransactionDetailAPI

urlpatterns = [
    path('', TransactionAPI.as_view()),
    path('<int:pk>/', TransactionDetailAPI.as_view()),
]
