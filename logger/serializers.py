from rest_framework import serializers

from .models import RequestLog


class RequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLog
        fields = ['timestamp', 'path', 'method', 'request_data',
                  'response_data', 'status_code', 'error_message']
