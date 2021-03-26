from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('signup/', views.SignUpView.as_view()),
    path('login_rtmp/', views.RTMPLoginView.as_view()),
]
