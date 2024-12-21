from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView, status


class HealthCheckAPI(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        content = {
            'status': 'OK',
            'message': 'System is healthy',
            'data': True,
            "options": {}
        }
        return Response(content, status=status.HTTP_200_OK)