import config

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.staticfiles.views import serve

from rest_framework.permissions import AllowAny

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

urlpatterns = [
    path('', serve, {'path': 'index.html'}),
    path('admin/', admin.site.urls),
    path('api/', include('apps.chat.urls')),
    path('api/auth/', include('apps.auth_api.urls')),
]

# add swagger ui view and dev related links

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title='ChatUP API',
            default_version=f'{settings.REST_API_VERSION}-{config.__version__}'
        ),

        url=settings.REST_API_DOCS_URL,
        public=True,
        permission_classes=(AllowAny,),
    )

    urlpatterns += [
        path('api/docs/', schema_view.with_ui(), name='docs'),
        path('dev/', TemplateView.as_view(template_name='dev.html')),
    ]
