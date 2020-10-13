from django.urls import path
from django.conf import settings
from django.views.generic import TemplateView

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'roles', views.RoleViewSet)
router.register(r'broadcasts', views.BroadcastViewSet)

urlpatterns = [
    path('general/lang/', views.LangView.as_view()),
    path('general/user/', views.UserView.as_view()),
    *router.urls,
]

if settings.DEBUG:
    # add websocket pages

    urlpatterns += [
        path('ws/rooms/', TemplateView.as_view(template_name='rooms.html'), name='rooms'),

        path('ws/rooms/<str:name>/', TemplateView.as_view(
            template_name='room.html',
            extra_context={'use_https': settings.REST_API_USE_HTTPS}
        )),
    ]
