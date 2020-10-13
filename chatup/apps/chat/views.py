from rest_framework import mixins, viewsets, permissions
from rest_framework.views import APIView, Response

from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

from . import models, serializers, permissions as own_permissions


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


class BroadcastViewSet(viewsets.ModelViewSet):
    """ User broadcasts viewset """

    queryset = models.Broadcast.objects.select_related('streamer').order_by('-created')
    serializer_class = serializers.BroadcastSerializer
    permission_classes = permissions.IsAuthenticated, own_permissions.IsBroadcastStreamer
    filterset_fields = 'title', 'streamer'  # 'streamer' filter means streamer id
