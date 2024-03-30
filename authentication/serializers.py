from django.contrib.auth.models import User
from rest_framework import serializers

from authentication.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'email', 'username', 'password']
