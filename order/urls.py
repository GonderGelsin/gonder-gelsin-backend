from django.urls import path

from .api import ActiveOrdersAPIView, OrderListCreateAPIView

urlpatterns = [
    path('', OrderListCreateAPIView.as_view()),
    path('active/', ActiveOrdersAPIView.as_view()),
    
    

]
