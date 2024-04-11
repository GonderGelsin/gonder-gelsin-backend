from django.urls import path

from .api import UserProfileDetailAPI

urlpatterns = [
    path("", UserProfileDetailAPI.as_view())    
]