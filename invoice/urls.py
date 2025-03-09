from django.urls import path

from .api import (BillingAddressAPI, BillingAddressDetailAPI,
                  BillingAddressSetDefaultAPI)

urlpatterns = [
    path("", BillingAddressAPI.as_view()),
    path("<int:pk>/", BillingAddressDetailAPI.as_view()),
    path("default/<int:pk>/", BillingAddressSetDefaultAPI.as_view()),
]
