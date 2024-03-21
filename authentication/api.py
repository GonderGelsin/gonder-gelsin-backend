import json

from rest_framework.response import Response
from rest_framework.views import status
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import CustomUserSerializer, CustomUserResponseSerializer

from django.conf import settings

class CustomUserAPI(APIView):

    def get(self , request):
        content = {
            'status': 'NOK',
            'message': 'Operation Failed.',
            'data': [],
            'options': {},
        }
        
        custom_users = CustomUser.objects.all()
        serializer = CustomUserResponseSerializer(custom_users, many=True)
        
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
        
        request_data = request.data
        serializer = CustomUserSerializer(data=request_data)
        
        if serializer.is_valid():
            serializer.save()
            content['status'] = 'OK'
            content['message'] = 'User Created Succesfully'

        
            return Response(content, status=status.HTTP_200_OK)
        
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
        