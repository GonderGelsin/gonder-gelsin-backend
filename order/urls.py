from django.urls import path

from .api import (ActiveOrdersAPIView, ComplatedOrdersAPIView,
                  OrderListCreateAPIView)

urlpatterns = [
    path('', OrderListCreateAPIView.as_view()),
    path('active/', ActiveOrdersAPIView.as_view()),
    path('complated/', ComplatedOrdersAPIView.as_view()),



]
