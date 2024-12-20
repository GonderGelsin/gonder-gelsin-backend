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

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not self.should_log_request(request.path):
            return self.get_response(request)

        start_time = time.time()

        request_body = None
        if request.body:
            try:
                request_body = json.loads(request.body)
            except json.JSONDecodeError:
                request_body = request.body.decode('utf-8')

        response = self.get_response(request)

        response_body = None
        if hasattr(response, 'content'):
            try:
                response_body = json.loads(response.content)
            except json.JSONDecodeError:
                response_body = response.content.decode('utf-8')

        duration = time.time() - start_time

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