from django.contrib.auth.models import User
from rest_framework import serializers

from authentication.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'password', 'turkish_id_number', 'first_name', 'last_name']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
