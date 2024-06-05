import json

from django.conf import settings
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, status

from authentication.models import CustomUser
from utils.utils import CustomErrorResponse, CustomSuccessResponse

from .serializers import UserProfileSerializer, UserProfileTestSerializer


class UserProfileDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        try:
            user = request.user
            if user:
                serializer = UserProfileSerializer(user)
                return CustomSuccessResponse(input_data={'profile': serializer.data}, status_code=status.HTTP_200_OK)

            return CustomErrorResponse(status_code=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return CustomErrorResponse(msj=str(e), status_code=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        request_data = request.data
        serializer = UserProfileSerializer(
            instance=request.user, data=request_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return CustomSuccessResponse(status_code=status.HTTP_200_OK)

        return CustomErrorResponse(status_code=status.HTTP_400_BAD_REQUEST)


class TestAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserProfileTestSerializer(users, many=True)
        return CustomSuccessResponse(input_data=serializer.data)


class UserNotificationAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user
        data = {
            'sms_notification': user.sms_notification,
            'email_notification': user.email_notification
        }
        return Response(data, status=status.HTTP_200_OK)

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
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user
        data = {
            'app_lang': user.app_lang
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        data = request.data

        if 'app_lang' in data:
            user.app_lang = data['app_lang']

        user.save()
        return Response(status=status.HTTP_200_OK)
