from django.contrib.auth.models import User
from rest_framework import serializers

from .models import BillingAddress


class BillingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        fields = '__all__'
