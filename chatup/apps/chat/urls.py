from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('roles', views.RoleViewSet)

urlpatterns = [
    path('general/lang/', views.LangView.as_view()),
    path('general/user/', views.UserView.as_view()),
    *router.urls,
]
