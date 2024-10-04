from django.urls import path

from .api import BillingAddressAPI, BillingAddressDetailAPI

urlpatterns = [
    path("", BillingAddressAPI.as_view()),
    path("<int:pk>/", BillingAddressDetailAPI.as_view()),
]
