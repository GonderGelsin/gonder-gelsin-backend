from django.urls import path

from .api import (NotificationDetail, NotificationListCreate, NotificationRead,
                  SendNotificationAPI)

urlpatterns = [
    path('', NotificationListCreate.as_view(), name='notification-list-create'),
    path('<int:pk>/', NotificationDetail.as_view(), name='notification-detail'),
    path('read/', NotificationRead.as_view(), name='notification-read'),
    path('send/', SendNotificationAPI.as_view(), name='notification-send'),

]
