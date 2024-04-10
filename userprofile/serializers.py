from django.contrib.auth.models import User
from rest_framework import serializers

from authentication.models import CustomUser


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ["full_name", "first_name", "last_name", "phone_number", "email", "turkish_id_number", "date_joined", "last_login"]



