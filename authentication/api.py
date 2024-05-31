import json
import random
import string
from logging import getLogger

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework_simplejwt.tokens import RefreshToken

from utils.utils import CustomErrorResponse, CustomSuccessResponse, send_email

from .models import CustomUser
from .serializers import TokenObtainSerializer, UserSerializer

logger = getLogger()


class UserSignUpAPI(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return CustomSuccessResponse(input_data={'user': serializer.data}, msj="User Created Successfully.", status_code=status.HTTP_201_CREATED)
        return CustomErrorResponse(msj=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class UserSignInAPI(APIView):
    permission_classes = []

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        if serializer.is_valid():

            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            response_data = {'token': token.key,
                             'user_id': user.pk, 'email': user.email}
            return CustomSuccessResponse(input_data=response_data, status_code=status.HTTP_200_OK)

        return CustomErrorResponse(msj={'error': serializer.errors}, status_code=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')
            user = get_object_or_404(CustomUser, email=email)
            send_email('Test Subject', 'This is a test email body.', user.email)
            
            email = EmailMessage('Test', 'Test', to=['umuttopalak@hotmail.com'])
            email.send()
            return CustomSuccessResponse()
        except Exception as e:
            return Response(data=str(e))

        # if user:
        #     # Generate token for password reset
        #     token = default_token_generator.make_token(user)

        #     # Build reset password link
        #     uid = urlsafe_base64_encode(force_bytes(user.pk))
        #     reset_link = f"https://gondergelsin.pythonanywhere.com/reset-password/{uid}/{token}/"

        #     # Send reset password email
        #     subject = "Reset your password"
        #     message = render_to_string(r'reset_password_email.html', {
        #         'reset_link': reset_link,
        #     })
        #     send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        #     return CustomSuccessResponse(msj="Password reset link has been sent to your email.", status_code=status.HTTP_200_OK)

        # return CustomErrorResponse(msj="User not found.", status_code=status.HTTP_404_NOT_FOUND)


class TestListAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response(data=[], status=status.HTTP_200_OK)