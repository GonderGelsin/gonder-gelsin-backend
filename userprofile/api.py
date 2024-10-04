import json

from django.conf import settings
from django.contrib.auth.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.models import CustomUser
from utils.utils import (CustomErrorResponse, CustomSuccessResponse,
                         send_notification)

from .serializers import UserProfileSerializer, UserProfileTestSerializer


class UserProfileDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get the authenticated user's profile details",
        responses={200: UserProfileSerializer, 400: "Bad Request"}
    )
    def get(self, request):
        try:
            user = request.user
            if user:
                serializer = UserProfileSerializer(user)
                return CustomSuccessResponse(input_data={'profile': serializer.data}, status_code=status.HTTP_200_OK)
            return CustomErrorResponse(status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return CustomErrorResponse(msj=str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Update the authenticated user's profile details",
        request_body=UserProfileSerializer,
        responses={200: "Profile updated successfully", 400: "Validation error"}
    )
    def put(self, request):
        request_data = request.data
        serializer = UserProfileSerializer(instance=request.user, data=request_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return CustomSuccessResponse(status_code=status.HTTP_200_OK)
        return CustomErrorResponse(status_code=status.HTTP_400_BAD_REQUEST)


class TestAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Test endpoint that retrieves all users and sends a test notification",
        responses={200: UserProfileTestSerializer(many=True)}
    )
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserProfileTestSerializer(users, many=True)
        print(send_notification("dd0MdIfRTQakTHGTt4hqXR:APA91bHSmZ-lkYdGj7YizmmvA07rl_9IDsTSLriwd1fM4iEPPuTtkihfVuGIRYF4pSF9oFmeD-ASdSzuEwO6mqKIUGG-CjdAEpCxG97wykRxxOhWb9q8SX1o06H1mLH-g0gSZnKmM7ZO"))
        return CustomSuccessResponse(input_data=serializer.data)


class UserNotificationAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get the user's notification preferences (SMS and Email)",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'sms_notification': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='SMS notification status'),
                'email_notification': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Email notification status'),
            }
        )}
    )
    def get(self, request):
        user = request.user
        data = {
            'sms_notification': user.sms_notification,
            'email_notification': user.email_notification
        }
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update the user's notification preferences (SMS and Email)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'sms_notification': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='SMS notification status'),
                'email_notification': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Email notification status'),
            }
        ),
        responses={204: "No Content"}
    )
    def put(self, request):
        user = request.user
        data = request.data

        if 'sms_notification' in data:
            user.sms_notification = data['sms_notification']
        if 'email_notification' in data:
            user.email_notification = data['email_notification']

        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserLanguageAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get the user's preferred language setting",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'app_lang': openapi.Schema(type=openapi.TYPE_STRING, description='App language'),
            }
        )}
    )
    def get(self, request):
        user = request.user
        data = {
            'app_lang': user.app_lang
        }
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update the user's preferred language setting",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'app_lang': openapi.Schema(type=openapi.TYPE_STRING, description='App language'),
            }
        ),
        responses={200: "Language updated successfully"}
    )
    def put(self, request):
        user = request.user
        data = request.data

        if 'app_lang' in data:
            user.app_lang = data['app_lang']

        user.save()
        return Response(status=status.HTTP_200_OK)
