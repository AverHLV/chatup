from rest_framework import generics, viewsets, permissions
from rest_framework.views import APIView, Response
from rest_framework.decorators import action

from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

from . import models, serializers, permissions as own_permissions


class ModelViewSetBase(viewsets.ModelViewSet):
    """ Custom viewset with a couple of helpers """

    serializer_action_classes: dict = {}

    def get_serializer_class(self):
        """ Look for serializer class in actions dictionary first """

        return self.serializer_action_classes.get(self.action) or super().get_serializer_class()

    def list_response(self, queryset):
        """ List action for custom queryset """

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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


class RoleView(generics.ListAPIView):
    """ User roles list view """

    queryset = models.Role.objects.order_by('sid')
    serializer_class = serializers.RoleSerializer


class BroadcastViewSet(ModelViewSetBase):
    """ User broadcasts viewset """

    queryset = models.Broadcast.objects.select_related('streamer').order_by('-created')
    serializer_class = serializers.BroadcastSerializer
    permission_classes = permissions.IsAuthenticated, own_permissions.IsBroadcastStreamer
    filterset_fields = 'title', 'is_active', 'streamer_id'

    serializer_action_classes = {
        'messages': serializers.MessageSerializer,
    }

    @action(methods=['GET'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def messages(self, request, pk):
        """ Get messages from specific broadcast """

        self.get_object()

        queryset = models.Message.objects \
            .filter(broadcast_id=pk) \
            .select_related('author', 'deleter') \
            .order_by('-created')

        return self.list_response(queryset)
