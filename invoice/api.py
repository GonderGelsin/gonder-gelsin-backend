import json
import logging
import random
import string
from logging import getLogger

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage, send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_yasg.utils import swagger_auto_schema
from fcm_django.models import FCMDevice
from rest_framework import status
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from utils.utils import CustomErrorResponse, CustomSuccessResponse

from .models import BillingAddress
from .serializers import BillingAddressSerializer


class BillingAddressAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(responses={200: BillingAddressSerializer(many=True)})
    def get(self, request):
        try:
            user = request.user
            if not user:
                return CustomErrorResponse(
                    error_code="USER_NOT_FOUND",
                    msj="User not found.",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

            addresses = BillingAddress.objects.filter(user=user)
            if not addresses.exists():
                return CustomErrorResponse(
                    error_code="NO_BILLING_ADDRESS_FOUND",
                    msj="No billing address found for the user.",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = BillingAddressSerializer(addresses, many=True)
            return CustomSuccessResponse(input_data={"data": serializer.data}, status_code=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return CustomErrorResponse(
                error_code="OBJECT_NOT_FOUND",
                msj="Billing address object not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(str(e))
            return CustomErrorResponse(
                error_code="INTERNAL_SERVER_ERROR",
                msj="An internal server error occurred.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(responses={200: BillingAddressSerializer(many=False)}, request_body=BillingAddressSerializer)
    def post(self, request):
        try:
            user = request.user
            if not user:
                return CustomErrorResponse(
                    error_code="USER_NOT_FOUND",
                    msj="User not found.",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

            data = request.data
            data['user'] = user.id
            serializer = BillingAddressSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return CustomSuccessResponse(input_data={"data": serializer.data}, status_code=status.HTTP_201_CREATED)
            else:
                return CustomErrorResponse(
                    error_code="VALIDATION_ERROR",
                    msj=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return CustomErrorResponse(
                error_code="INTERNAL_SERVER_ERROR",
                msj="An internal server error occurred.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BillingAddressDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        pass

    def put(self, request):
        pass

    def delete(self, request):
        pass
