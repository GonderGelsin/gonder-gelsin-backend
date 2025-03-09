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

    def get_object(self, pk, user):
        # Verilen pk ve kullanıcıya ait fatura adresini getirir, yoksa 404 hatası döner.
        return get_object_or_404(BillingAddress, pk=pk, user=user)

    @swagger_auto_schema(
        responses={200: BillingAddressSerializer()}
    )
    def get(self, request, pk):
        try:
            user = request.user
            billing_address = self.get_object(pk, user)
            serializer = BillingAddressSerializer(billing_address)
            return CustomSuccessResponse(
                input_data={"data": serializer.data},
                status_code=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return CustomErrorResponse(
                error_code="BILLING_ADDRESS_NOT_FOUND",
                msj="Billing address not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(str(e))
            return CustomErrorResponse(
                error_code="INTERNAL_SERVER_ERROR",
                msj="An internal server error occurred.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        request_body=BillingAddressSerializer,
        responses={200: BillingAddressSerializer()}
    )
    def put(self, request, pk):
        try:
            user = request.user
            billing_address = self.get_object(pk, user)
            serializer = BillingAddressSerializer(
                billing_address, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return CustomSuccessResponse(
                    input_data={"data": serializer.data},
                    status_code=status.HTTP_200_OK
                )
            else:
                return CustomErrorResponse(
                    error_code="VALIDATION_ERROR",
                    msj=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        except ObjectDoesNotExist:
            return CustomErrorResponse(
                error_code="BILLING_ADDRESS_NOT_FOUND",
                msj="Billing address not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(str(e))
            return CustomErrorResponse(
                error_code="INTERNAL_SERVER_ERROR",
                msj="An internal server error occurred.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        responses={204: "Billing address deleted successfully."}
    )
    def delete(self, request, pk):
        try:
            user = request.user
            billing_address = self.get_object(pk, user)
            billing_address.delete()
            return CustomSuccessResponse(
                input_data={
                    "message": "Billing address deleted successfully."},
                status_code=status.HTTP_204_NO_CONTENT
            )
        except ObjectDoesNotExist:
            return CustomErrorResponse(
                error_code="BILLING_ADDRESS_NOT_FOUND",
                msj="Billing address not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(str(e))
            return CustomErrorResponse(
                error_code="INTERNAL_SERVER_ERROR",
                msj="An internal server error occurred.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


from drf_yasg import openapi


class BillingAddressSetDefaultAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="Billing address primary key",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: BillingAddressSerializer()}
    )
    def get(self, request, pk):
        try:
            user = request.user
            # İlgili fatura adresini, kullanıcının kayıtları arasından getir.
            billing_address = get_object_or_404(BillingAddress, pk=pk, user=user)

            # Kullanıcının tüm fatura adreslerinin is_default değerini False yap.
            BillingAddress.objects.filter(user=user).update(is_default=False)

            # Seçilen adresi varsayılan olarak işaretle.
            billing_address.is_default = True
            billing_address.save()

            serializer = BillingAddressSerializer(billing_address)
            return CustomSuccessResponse(
                input_data={"data": serializer.data},
                status_code=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return CustomErrorResponse(
                error_code="BILLING_ADDRESS_NOT_FOUND",
                msj="Billing address not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(str(e))
            return CustomErrorResponse(
                error_code="INTERNAL_SERVER_ERROR",
                msj="An internal server error occurred.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
