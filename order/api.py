from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Order
from .serializers import OrderSerializer


class OrderListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get a list of orders with optional filters",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="Order status", type=openapi.TYPE_STRING),
            openapi.Parameter('date', openapi.IN_QUERY, description="Order date", type=openapi.TYPE_STRING),
        ],
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request):
        filters = {}
        for param, value in request.query_params.items():
            filter_key = f"{param}__icontains"
            filters[filter_key] = value

        orders = Order.objects.filter(Q(**filters), user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new order",
        request_body=OrderSerializer,
        responses={201: OrderSerializer, 400: "Validation Error"}
    )
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    @swagger_auto_schema(
        operation_description="Retrieve an order",
        responses={200: OrderSerializer, 400: "Not Found"})
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        serializer = OrderSerializer(order, many=False)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActiveOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get a list of active orders (status: P or O)",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request):
        orders = Order.objects.filter(status__in=['P', 'O'], user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class ComplatedOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get a list of completed orders (status: C)",
        responses={200: OrderSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            orders = Order.objects.filter(status__exact='C', user=request.user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(data={"exp": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateOrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Update the status of an order. Status transitions: P -> O -> C",
        responses={
            200: "Order status updated",
            400: "Order already delivered or invalid status"
        }
    )
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        if order.status == 'P':
            order.status = 'O'
        elif order.status == 'O':
            order.status = 'C'
        else:
            return Response(data={"exp": "Order already delivered"}, status=status.HTTP_400_BAD_REQUEST)

        order.save()
        return Response(data={"status": "Done"}, status=status.HTTP_200_OK)


class DeleteOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Delete an order by its ID",
        responses={204: "Order deleted", 404: "Order not found"}
    )
    def delete(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
