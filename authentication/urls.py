from django.urls import path
from authentication.api import CustomUserAPI 

urlpatterns = [
    path('', CustomUserAPI.as_view()),
]
