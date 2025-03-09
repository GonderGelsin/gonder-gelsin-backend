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
            return CustomErrorResponse(msj={"error": "Message body is required"}, status_code=status.HTTP_400_BAD_REQUEST)

        if not hasattr(settings, 'FIREBASE_APP') or settings.FIREBASE_APP is None:
            Notification.objects.create(
                user=user,
                title=title,
                message=message_body
            )
            logger.warning(
                "Firebase yapılandırması bulunamadı. Bildirim sadece veritabanına kaydedildi.")
            return CustomSuccessResponse(input_data={"warning": "Notification saved to database but not sent to devices due to Firebase configuration issue"}, status_code=status.HTTP_200_OK)

        devices = FCMDevice.objects.filter(user=user)

        if not devices.exists():
            Notification.objects.create(
                user=user,
                title=title,
                message=message_body
            )
            return CustomSuccessResponse(input_data={"warning": "No devices registered for this user. Notification saved to database."}, status_code=status.HTTP_200_OK)

        success_count = 0
        error_messages = []

        for device in devices:
            try:
                message = fbm.Message(
                    notification=fbm.Notification(
                        title=title, body=message_body),
                    token=device.registration_id)

                response = fbm.send(message)
                logger.warning(response)
                success_count += 1

                Notification.objects.create(
                    user=user,
                    title=title,
                    message=message_body
                )

            except Exception as e:
                logger.error(
                    f"Failed to send message to device {device.registration_id}: {str(e)}")
                error_messages.append(str(e))

        if success_count > 0:
            return CustomSuccessResponse(input_data={"success": f"Successfully sent to {success_count} devices"}, status_code=status.HTTP_200_OK)
        elif error_messages:
            return CustomErrorResponse(msj={"error": f"Failed to send message: {error_messages}"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return CustomErrorResponse(msj={"error": "No messages were sent"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendGeneralNotificationAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Send general notification to all registered devices",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Notification title'),
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Notification message'),
            },
            required=['message']
        ),
        responses={
            200: "Notification sent successfully",
            400: "Message body is required",
            403: "Invalid or missing API key",
            500: "Failed to send message"
        }
    )
    def post(self, request):
        x_api_key = request.headers.get("x-api-key")
        expected_api_key = getattr(settings, "X_API_KEY", None)
        if not x_api_key or x_api_key != expected_api_key:
            return CustomErrorResponse(
                msj={"error": "Invalid or missing API key"},
                status_code=status.HTTP_403_FORBIDDEN
            )

        request_data = request.data
        title = request_data.get("title", "Gönder Gelsin")
        message_body = request_data.get("message")

        if not message_body:
            return CustomErrorResponse(
                msj={"error": "Message body is required"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if not hasattr(settings, 'FIREBASE_APP') or settings.FIREBASE_APP is None:
            logger.warning(
                "Firebase yapılandırması bulunamadı. Genel bildirim gönderilemedi.")
            return CustomErrorResponse(
                msj={
                    "error": "Firebase configuration not available. Cannot send general notifications."},
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        devices = FCMDevice.objects.all()

        if not devices.exists():
            return CustomErrorResponse(
                msj={"error": "No devices found in the system."},
                status_code=status.HTTP_404_NOT_FOUND
            )

        sended_notification_count = 0
        error_count = 0

        for device in devices:
            try:
                if not device.registration_id:
                    continue

                message = fbm.Message(
                    notification=fbm.Notification(
                        title=title, body=message_body
                    ),
                    token=device.registration_id
                )
                response = fbm.send(message)
                logger.warning(f"Device: {device.registration_id}, Response: {response}")
                sended_notification_count += 1

                if device.user:
                    Notification.objects.create(
                        user=device.user,
                        title=title,
                        message=message_body
                    )
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to send message to device {device.registration_id}: {str(e)}")

        response_data = {
            "total_device_count": devices.count(),
            "notification_sent_count": sended_notification_count,
            "error_count": error_count
        }

        if sended_notification_count > 0:
            return CustomSuccessResponse(
                status_code=status.HTTP_200_OK,
                input_data=response_data
            )
        else:
            return CustomErrorResponse(
                msj={"error": "Failed to send notifications to any device.",
                     "details": response_data},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
