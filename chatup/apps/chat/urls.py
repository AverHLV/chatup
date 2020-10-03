from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('roles', views.RoleViewSet)

urlpatterns = [
    path('user/', views.UserView.as_view()),
    *router.urls,
]
