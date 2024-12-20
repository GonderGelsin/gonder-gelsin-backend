from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from utils.utils import CustomErrorResponse, CustomSuccessResponse

from .models import RequestLog
from .serializers import RequestLogSerializer


class CustomPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class RequestLogAPI(APIView):
    permission_classes = []
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['method', 'status_code']
    search_fields = ['path', 'error_message']
    ordering_fields = ['timestamp', 'duration', 'status_code']
    ordering = ['-timestamp']
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_description="Get all request logs with filtering options",
        manual_parameters=[
            openapi.Parameter('method', openapi.IN_QUERY,
                              description="Filter by HTTP method", type=openapi.TYPE_STRING),
            openapi.Parameter('status_code', openapi.IN_QUERY,
                              description="Filter by status code", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY,
                              description="Search in path and error message", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY,
                              description="Order by field (e.g. -timestamp)", type=openapi.TYPE_STRING),
        ],
        responses={200: RequestLogSerializer(many=True)}
    )
    def get(self, request):
        try:
            queryset = RequestLog.objects.all()

            for backend in self.filter_backends:
                queryset = backend().filter_queryset(request, queryset, self)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)

            serializer = RequestLogSerializer(page, many=True)

            pagination_meta = {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
            }

            return CustomSuccessResponse(
                input_data=serializer.data,
                status_code=status.HTTP_200_OK,
                input_options=pagination_meta
            )

        except Exception as e:
            return CustomErrorResponse(
                msj=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )


class RequestLogDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Get a specific request log by ID",
        responses={200: RequestLogSerializer}
    )
    def get(self, request, log_id):
        try:
            log = RequestLog.objects.get(id=log_id)
            serializer = RequestLogSerializer(log)
            return CustomSuccessResponse(
                input_data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except RequestLog.DoesNotExist:
            return CustomErrorResponse(
                msj="Log not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
