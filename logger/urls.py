from django.urls import path

from .api import RequestLogAPI, RequestLogDetailAPI

urlpatterns = [
    path("logs/", RequestLogAPI.as_view()),
    path("logs/<int:log_id>/", RequestLogDetailAPI.as_view()),
]