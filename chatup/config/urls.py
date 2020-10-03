from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.chat.urls')),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(title='ChatUP API', default_version=settings.REST_API_VERSION),
        public=True,
        permission_classes=(IsAuthenticated,),
    )

    urlpatterns.append(
        path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='docs')
    )
