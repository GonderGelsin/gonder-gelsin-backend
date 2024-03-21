from rest_framework import serializers
from authentication.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = '__all__'

class CustomUserResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('name', 'surname', 'email', 'phone')
