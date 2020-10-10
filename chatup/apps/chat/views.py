from rest_framework import mixins, viewsets
from rest_framework.views import APIView, Response

from django.conf import settings
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema

from . import models, serializers


def rooms(request):
    """ Chat rooms view """

    return render(request, 'rooms.html')


def room(request, name: str):
    """ Chat room view """

    return render(request, 'room.html', {'name': name, 'use_https': settings.REST_API_USE_HTTPS})


class LangView(APIView):
    """
    Retrieve language cookie name and supported languages with
    human-readable representations
    """

    @staticmethod
    def get(_request):
        data = {
            lang[0]: {'repr': lang[1], 'default': lang[0] == settings.LANGUAGE_CODE}
            for lang in settings.LANGUAGES
        }

        return Response({'cookie_name': settings.LANGUAGE_COOKIE_NAME, 'languages': data})


class UserView(APIView):
    """ Get current user info """

    # noinspection PyTypeChecker

    @swagger_auto_schema(responses={'200': serializers.UserSerializer})
    def get(self, request):
        serializer = serializers.UserSerializer(
            request.user,
            context={'request': request, 'view': self}
        )

        return Response(serializer.data)


class RoleViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ User roles viewset """

    queryset = models.Role.objects.order_by('sid')
    serializer_class = serializers.RoleSerializer
