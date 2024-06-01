from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer


class OrderListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        filters = {}
        for param, value in request.query_params.items():
            filter_key = f"{param}__icontains"
            filters[filter_key] = value

        orders = Order.objects.filter(Q(**filters), user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActiveOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        orders = Order.objects.filter(status__in=['P', 'O'], user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class ComplatedOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        try:
            orders = Order.objects.filter(status__exact='C', user=request.user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(data={"exp" : str(e)})

class UpdateOrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

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
