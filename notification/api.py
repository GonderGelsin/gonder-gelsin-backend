import os
from logging import getLogger

import firebase_admin.messaging as fbm
from django.conf import settings
from django.http import JsonResponse
from dotenv import load_dotenv
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from fcm_django.models import FCMDevice
from pyfcm import FCMNotification
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.models import CustomUser
from utils.utils import CustomErrorResponse, CustomSuccessResponse

from .models import Notification
from .serializers import NotificationSerializer

logger = getLogger("my_logger")


class NotificationListCreate(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get the list of notifications for the authenticated user",
        responses={200: NotificationSerializer(many=True)}
    )
    def get(self, request, format=None):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new notification",
        request_body=NotificationSerializer,
        responses={201: NotificationSerializer, 400: "Validation Error"}
    )
    def post(self, request, format=None):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationDetail(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get a specific notification by its ID",
        responses={200: NotificationSerializer, 404: "Notification not found"}
    )
    def get(self, request, pk, format=None):
        notification = self.get_object(pk, request.user)
        if notification is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a specific notification by its ID",
        request_body=NotificationSerializer,
        responses={200: NotificationSerializer,
                   404: "Notification not found", 400: "Validation Error"}
    )
    def put(self, request, pk, format=None):
        notification = self.get_object(pk, request.user)
        if notification is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(notification, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a specific notification by its ID",
        responses={204: "Notification deleted", 404: "Notification not found"}
    )
    def delete(self, request, pk, format=None):
        notification = self.get_object(pk, request.user)
        if notification is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationRead(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Mark a notification as read",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Notification ID'),
            }
        ),
        responses={200: "Notification marked as read",
                   404: "Notification not found"}
    )
    def post(self, request, format=None):
        notification_id = request.data.get('id')
        try:
            notification = Notification.objects.get(
                id=notification_id, user=request.user)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marked as read'}, status=status.HTTP_200_OK)


class SendNotificationAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Send a notification to the user's registered devices",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Notification title'),
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Notification message'),
            },
            required=['message']
        ),
        responses={200: "Notification sent successfully",
                   400: "Message body is required", 500: "Failed to send message"}
    )
    def post(self, request):
        request_data = request.data
        user = request.user
        title = request_data.get("title", "Gönder Gelsin")
        message_body = request_data.get("message")

        if not message_body:
            return CustomErrorResponse(input_data={"error": "Message body is required"}, status_code=status.HTTP_400_BAD_REQUEST)

        devices = FCMDevice.objects.filter(user=user)

        for device in devices:
            try:
                message = fbm.Message(
                    notification=fbm.Notification(
                        title=title, body=message_body),
                    token=device.registration_id
                )
                fbm.send(message)
            except Exception as e:
                logger.error(
                    f"Failed to send message to device {device.registration_id}: {str(e)}")
                return Response({"error": f"Failed to send message: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return CustomSuccessResponse(status_code=status.HTTP_200_OK)
