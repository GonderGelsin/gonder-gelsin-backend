import json
from logging import getLogger

from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework_simplejwt.tokens import RefreshToken

from utils.utils import CustomErrorResponse, CustomSuccessResponse

from .serializers import TokenObtainSerializer, UserSerializer

logger = getLogger()


class UserSignUpAPI(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'user': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSignInAPI(APIView):
    permission_classes = []

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        if serializer.is_valid():
        
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            })

        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
