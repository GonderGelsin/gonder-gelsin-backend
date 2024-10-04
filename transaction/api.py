from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.utils import CustomErrorResponse, CustomSuccessResponse

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        operation_description="Get a list of transactions for the authenticated user",
        responses={200: TransactionSerializer(many=True)}
    )
    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return CustomSuccessResponse(input_data=serializer.data, status_code=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new transaction",
        request_body=TransactionSerializer,
        responses={201: TransactionSerializer, 400: "Validation Error"}
    )
    def post(self, request):
        data = request.data
        data['user'] = request.user.id
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return CustomSuccessResponse(input_data=serializer.data, status_code=status.HTTP_201_CREATED)
        return CustomErrorResponse(error_code=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class TransactionDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        operation_description="Get details of a specific transaction by its ID",
        responses={200: TransactionSerializer, 404: "Transaction not found"}
    )
    def get(self, request, pk):
        try:
            transaction = Transaction.objects.get(pk=pk, user=request.user)
        except Transaction.DoesNotExist:
            return CustomErrorResponse(msj="Transaction not found", status_code=status.HTTP_404_NOT_FOUND)
        serializer = TransactionSerializer(transaction)
        return CustomSuccessResponse(input_data=serializer.data, status_code=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a specific transaction",
        request_body=TransactionSerializer,
        responses={200: TransactionSerializer, 400: "Validation Error", 404: "Transaction not found"}
    )
    def put(self, request, pk):
        try:
            transaction = Transaction.objects.get(pk=pk, user=request.user)
        except Transaction.DoesNotExist:
            return CustomErrorResponse(msj="Transaction not found", status_code=status.HTTP_404_NOT_FOUND)
        data = request.data
        serializer = TransactionSerializer(transaction, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return CustomSuccessResponse(input_data=serializer.data, status=status.HTTP_200_OK)
        return CustomErrorResponse(error_code=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a specific transaction by its ID",
        responses={204: 'No Content', 404: "Transaction not found"}
    )
    def delete(self, request, pk):
        try:
            transaction = Transaction.objects.get(pk=pk, user=request.user)
        except Transaction.DoesNotExist:
            return CustomErrorResponse(msj="Transaction not found", status_code=status.HTTP_404_NOT_FOUND)
        transaction.delete()
        return CustomSuccessResponse(status_code=status.HTTP_204_NO_CONTENT)
