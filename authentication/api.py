import json

from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, status

from .models import CustomUser
from .serializers import CustomUserSerializer, UserSerializer


class CustomUserAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get(self, request):
        content = {
            'status': 'NOK',
            'message': 'Operation Failed.',
            'data': [],
            'options': {},
        }

        custom_users = User.objects.all()
        serializer = UserSerializer(custom_users, many=True)

        content['data'] = serializer.data
        content['status'] = 'OK'
        content['message'] = "User Retrieved Successfully."

        return Response(content, status=status.HTTP_200_OK)

    def post(self, request):
        content = {
            'status': 'NOK',
            'message': 'Operation Failed.',
            'data': [],
            'options': {},
        }

        custom_users = User.objects.first()
        serializer = UserSerializer(custom_users, many=False)

        content['data'] = serializer.data
        content['status'] = 'OK'
        content['message'] = "User Retrieved Successfully."

        return Response(content, status=status.HTTP_200_OK)


class UserSignUpAPI(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=request.data['username'])
            user.set_password(request.data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return Response({'token': token.key, 'user': serializer.data})
        return Response(serializer.errors, status=status.HTTP_200_OK)


class UserSignInAPI(APIView):

    def post(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        if not user.check_password(request.data['password']):
            return Response("missing user", status=status.HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response({'token': token.key, 'user': serializer.data})


class UserTokenTestAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def test_token(request):
        return Response("passed!")
