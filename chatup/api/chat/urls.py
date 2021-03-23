from django.urls import path
from django.conf import settings
from django.views.generic import TemplateView

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'broadcasts', views.BroadcastViewSet)
router.register(r'images', views.ImageViewSet)
router.register(r'users', views.UserControlViewSet)

urlpatterns = [
    path('roles/', views.RoleView.as_view()),
    path('general/lang/', views.LangView.as_view()),
    path('general/user/', views.UserView.as_view()),
    *router.urls,
]

# add websocket pages

if settings.DEBUG:
    urlpatterns += [
        path('ws/rooms/', TemplateView.as_view(template_name='rooms.html'), name='rooms'),
        path('ws/rooms/<int:id>/', TemplateView.as_view(
            template_name='room.html',
            extra_context={'use_https': settings.REST_API_USE_HTTPS}
        )),
    ]
