from django.urls import path

from .api import SendGeneralNotificationAPI

urlpatterns = [
    path('general/send/', SendGeneralNotificationAPI.as_view(), name='general-notification-send'),

]
