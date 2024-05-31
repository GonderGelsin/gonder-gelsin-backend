from django.urls import path

from .api import OrderListCreateAPIView

urlpatterns = [
    path('', OrderListCreateAPIView.as_view()),

]
