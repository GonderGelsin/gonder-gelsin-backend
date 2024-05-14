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

from .serializers import UserProfileSerializer


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
        serializer = UserProfileSerializer(users, many=True)
        return CustomSuccessResponse(input_data=serializer.data)
    
