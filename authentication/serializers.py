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


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        phone_or_email = attrs.get("username")
        password = attrs.get("password")

        if '@' in phone_or_email:
            user = CustomUser.objects.filter(email=phone_or_email).first()
        else:
            user = CustomUser.objects.filter(phone_number=phone_or_email).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError("Invalid email/phone_number or password")

        attrs["user"] = user
        return attrs
