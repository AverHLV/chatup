from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from rest_framework.permissions import AllowAny

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html')),
    path('admin/', admin.site.urls),
    path('api/', include('apps.chat.urls')),
    path('api/auth/', include('apps.auth_api.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(title='ChatUP API', default_version=settings.REST_API_VERSION),
        url=settings.REST_API_DOCS_URL,
        public=True,
        permission_classes=(AllowAny,),
    )

    urlpatterns.append(
        path('api/docs/', schema_view.with_ui(), name='docs')
    )
