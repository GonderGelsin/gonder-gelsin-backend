# logger/middleware.py
import json
import time
from typing import Any

from django.http import HttpRequest, HttpResponse

from .models import RequestLog


class RequestResponseLogMiddleware:
    EXCLUDED_PATHS = [
        '/logger/',
        '/swagger/',
        '/redoc/',
        '/api/schema/',
        '/favicon.ico/',
        '/robots.txt/',
        '/sitemap.xml/',
        '/favicon-32x32.png/',
        '/favicon-16x16.png/',
        '/site.webmanifest/',
        '/apple-touch-icon.png/',
        '/apple-touch-icon-precomposed.png/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def should_log_request(self, path: str) -> bool:
        return not any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS)

    def get_request_body(self, request):
        try:
            if request.body:
                if isinstance(request.body, bytes):
                    return json.loads(request.body.decode('utf-8'))
                return json.loads(request.body)
        except json.JSONDecodeError:
            if hasattr(request, 'POST'):
                return dict(request.POST.items())
        return None

    def get_response_body(self, response):
        try:
            if hasattr(response, 'content'):
                if isinstance(response.content, bytes):
                    return json.loads(response.content.decode('utf-8'))
                return json.loads(response.content)
        except json.JSONDecodeError:
            if hasattr(response, 'data'):
                return response.data
        return None

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not self.should_log_request(request.path):
            return self.get_response(request)

        start_time = time.time()

        request_body = self.get_request_body(request)
        response = self.get_response(request)
        response_body = self.get_response_body(response)
        duration = time.time() - start_time

        # Hassas verileri maskele
        if request_body and isinstance(request_body, dict):
            if 'password' in request_body:
                request_body['password'] = '********'
            if 'id_token' in request_body:
                request_body['id_token'] = '********'

        RequestLog.objects.create(
            path=request.path,
            method=request.method,
            request_data=request_body,
            response_data=response_body,
            status_code=response.status_code,
            duration=duration,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            error_message=getattr(response, 'error_message', None)
        )

        return response