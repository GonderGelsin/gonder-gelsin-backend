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


class UserCompleteProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['phone_number', 'turkish_id_number', 'password']

    def validate_turkish_id_number(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("Turkish ID number must be 11 digits")
        return value

    def validate_phone_number(self, value):
        if not value.startswith('+') or not value[1:].isdigit():
            raise serializers.ValidationError("Phone number must start with '+' followed by digits")
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Önce diğer alanları güncelle
        instance = super().update(instance, validated_data)
        
        # Şifreyi güncelle
        if password:
            instance.set_password(password)
            instance.save()
        
        return instance
