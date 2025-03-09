"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .api import HealthCheckAPI

# Create a more explicit schema view with stronger public access settings
public_schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="API Documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
    url='https://api.gondergelsin.info'
)

# Create custom view to redirect to Swagger UI


def swagger_redirect(request):
    return HttpResponse("""
    <html>
        <head>
            <meta http-equiv="refresh" content="0;URL='/swagger/'" />
        </head>
        <body>
            <p>Redirecting to Swagger UI...</p>
        </body>
    </html>
    """)


urlpatterns = [
    path('', swagger_redirect, name='swagger-redirect'),
    path('swagger/', public_schema_view.with_ui('swagger',cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', public_schema_view.with_ui('redoc',cache_timeout=0), name='schema-redoc'),
    path('health-check/', HealthCheckAPI.as_view(), name='health-check'),

    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('user/', include('userprofile.urls')),
    path('user/notification/', include('notification.user_urls')),
    path('notification/', include('notification.urls')),
    path("transaction/", include('transaction.urls')),
    path("order/", include('order.urls')),
    path("invoice/", include('invoice.urls')),
    path('logger/', include('logger.urls')),

]

# Add static file serving for production
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
