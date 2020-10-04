from rest_framework import mixins, viewsets
from rest_framework.views import APIView, Response

from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

from . import models, serializers


class LangView(APIView):
    """ Retrieve supported languages with human-readable representations """

    @staticmethod
    def get(_request):
        data = {
            lang[0]: {'repr': lang[1], 'default': lang[0] == settings.LANGUAGE_CODE}
            for lang in settings.LANGUAGES
        }

        return Response(data)


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
