import json
import random
import string
from logging import getLogger

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from fcm_django.models import FCMDevice
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from utils.utils import CustomErrorResponse, CustomSuccessResponse, send_email

from .models import CustomUser
from .serializers import TokenObtainSerializer, UserSerializer

logger = getLogger()


class UserSignUpAPI(APIView):
    permission_classes = []

    @swagger_auto_schema(
        operation_description="User sign-up endpoint",
        request_body=UserSerializer,
        responses={201: 'User Created Successfully', 400: 'Validation Error'}
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return CustomSuccessResponse(input_data={'user': serializer.data}, msj="User Created Successfully.", status_code=status.HTTP_201_CREATED)
        return CustomErrorResponse(msj=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class UserSignInAPI(APIView):
    permission_classes = []

    @swagger_auto_schema(
        operation_description="User sign-in endpoint",
        request_body=TokenObtainSerializer,
        responses={200: 'Authentication Successful',
                   400: 'Authentication Error'}
    )
    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)
            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.pk,
                'email': user.email
            }

            return CustomSuccessResponse(input_data=response_data, status_code=status.HTTP_200_OK)

        return CustomErrorResponse(msj={'error': serializer.errors}, status_code=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPI(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Password reset request endpoint",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'email': openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={200: 'Password Reset Email Sent', 404: 'User Not Found'}
    )
    def post(self, request):
        try:
            email = request.data.get('email')
            user = get_object_or_404(CustomUser, email=email)
            send_email('Test Subject',
                       'This is a test email body.', user.email)
            return CustomSuccessResponse()
        except Exception as e:
            return Response(data=str(e))


class UserDeviceAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get the list of device tokens for the authenticated user",
        responses={200: 'Device tokens retrieved successfully'}
    )
    def get(self, request):
        user = request.user
        devices = FCMDevice.objects.filter(user=user)
        device_tokens = [device.registration_id for device in devices]
        return CustomSuccessResponse(input_data={"device_tokens": device_tokens}, status_code=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Register a new device token for the authenticated user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'device_token': openapi.Schema(type=openapi.TYPE_STRING, description="FCM device token"),
                'device_type': openapi.Schema(type=openapi.TYPE_STRING, description="Device type (android, ios, web)")
            }
        ),
        responses={200: 'Device token registered successfully',
                   400: 'Device token is required'}
    )
    def post(self, request):
        request_data = request.data
        device_token = request_data.get('device_token')
        device_type = request_data.get('device_type', 'android')

        if not device_token:
            return CustomErrorResponse(input_data={"error": "Device token is required"}, status_code=status.HTTP_400_BAD_REQUEST)

        user = request.user
        device, created = FCMDevice.objects.get_or_create(
            user=user,
            registration_id=device_token,
            defaults={'type': device_type},
        )

        if not created:
            device.type = device_type
            device.save()

        return CustomSuccessResponse(status_code=status.HTTP_200_OK)


# Google ile giriş API'si
@swagger_auto_schema(
    method='post',
    operation_description="Google Sign-In API",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id_token': openapi.Schema(type=openapi.TYPE_STRING, description='Google idToken'),
        },
        required=['id_token']
    ),
    responses={
        200: openapi.Response(
            description="Google Sign-In Successful",
            examples={
                "application/json": {
                    "refresh": "JWT_REFRESH_TOKEN",
                    "access": "JWT_ACCESS_TOKEN",
                    "user_id": 1,
                    "email": "user@example.com"
                }
            }
        ),
        400: openapi.Response(description="Invalid Token")
    }
)
@api_view(['POST'])
def google_sign_in(request):
    try:
        id_token_received = request.data.get('id_token')

        if not id_token_received:
            return Response({'error': 'id_token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        idinfo = id_token.verify_oauth2_token(
            id_token_received, google_requests.Request(), settings.GOOGLE_CLIENT_ID)

        if 'email' not in idinfo:
            return Response({'error': 'Google token does not contain email'}, status=status.HTTP_400_BAD_REQUEST)

        email = idinfo['email']
        user = CustomUser.objects.filter(email=email).first()
        print(email)
        print(user)
        if user:
            refresh = RefreshToken.for_user(user)
            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.pk,
                'email': user.email,
            }

            return CustomSuccessResponse(input_data=response_data, status_code=status.HTTP_200_OK)
        return CustomErrorResponse(status_code=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return CustomErrorResponse(msj=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # except ValueError as e:
    #     return Response({'error': f"Invalid token : {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    # except Exception as e:
    #     return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
