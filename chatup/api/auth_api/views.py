from django.contrib.auth import login, logout
from django.utils.translation import gettext as _

from rest_framework import status, permissions, exceptions
from rest_framework.views import APIView, Response

from drf_yasg.utils import swagger_auto_schema

from api.chat.models import Broadcast, Role
from . import serializers


class LoginView(APIView):
    """ Log in with credentials """

    permission_classes = permissions.AllowAny,

    @swagger_auto_schema(
        request_body=serializers.LoginSerializer,
        responses={
            '200': 'Successfully logged in',
            '400': 'Wrong credentials or user is inactive or already logged in',
        }
    )
    def post(self, request):
        if request.user.is_authenticated:
            return Response({'detail': _('You are already logged in.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.LoginSerializer(data=request.data, context={'request': request, 'view': self})
        serializer.is_valid(raise_exception=True)
        login(request, serializer.user)
        return Response({'detail': _('Successfully logged in.')})


class LogoutView(APIView):
    @staticmethod
    def get(request):
        logout(request)
        return Response({'detail': _('Successfully logged out.')})


class SignUpView(APIView):
    """ Create a new user instance and log in with the given data """

    permission_classes = permissions.AllowAny,

    @swagger_auto_schema(
        request_body=serializers.SignUpSerializer,
        responses={
            '200': 'Successfully registered and logged in',
            '400': 'Validation failed',
        }
    )
    def post(self, request):
        if request.user.is_authenticated:
            return Response({'detail': _('You are already logged in.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.SignUpSerializer(data=request.data, context={'request': request, 'view': self})
        serializer.is_valid(raise_exception=True)
        login(request, serializer.save())
        return Response({'detail': _('Successfully registered and logged in.')})


class RTMPLoginView(APIView):
    """ RTMP server login view ('on_publish' callback) """

    permission_classes = permissions.AllowAny,

    @swagger_auto_schema(request_body=serializers.LoginSerializer)
    def post(self, request):
        broadcast_id = self.to_int(request.data.get('name'))
        if not broadcast_id:
            raise exceptions.ValidationError({'name': _('Value not found or invalid.')})

        serializer = serializers.LoginSerializer(data=request.data, context={'request': request, 'view': self})
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        if user.role.sid != Role.SIDS.STREAMER:
            raise exceptions.PermissionDenied

        broadcast = Broadcast.objects.filter(id=broadcast_id, is_active=True, streamer_id=user.id)
        if not broadcast.exists():
            raise exceptions.ValidationError({'name': _('Broadcast not found.')})

        return Response({'detail': _('Publishing allowed.')})

    @staticmethod
    def to_int(value) -> (int, None):
        try:
            return int(value)
        except (ValueError, TypeError, OverflowError):
            return
