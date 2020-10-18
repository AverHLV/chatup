from rest_framework import generics, viewsets, permissions
from rest_framework.views import APIView, Response
from rest_framework.decorators import action

from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from . import models, serializers, permissions as own_permissions

author_param = openapi.Parameter(
    'author_id',
    openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    description='Author filter'
)


class ModelViewSetBase(viewsets.ModelViewSet):
    """ Custom viewset with a couple of helpers """

    serializer_action_classes: dict = {}
    action_filterset_fields: dict = {}

    def get_serializer_class(self):
        """ Look for serializer class in actions dictionary first """

        return self.serializer_action_classes.get(self.action) or super().get_serializer_class()

    def get_filters(self, request) -> dict:
        """ Build filters for custom actions """

        filters = {}

        for field in self.action_filterset_fields[self.action]:
            value = request.query_params.get(field, None)

            if value is not None:
                filters[field] = value

        return filters

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

    permission_classes = (
        own_permissions.IsAuthenticatedOrGET,
        own_permissions.IsBroadcastStreamer,
        own_permissions.IsBroadcastInactive,
    )

    filterset_fields = 'title', 'is_active', 'streamer_id'

    serializer_action_classes = {
        'messages': serializers.MessageSerializer,
    }

    action_filterset_fields = {
        'messages': ['author_id'],
    }

    @swagger_auto_schema(manual_parameters=[author_param])
    @action(methods=['GET'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def messages(self, request, pk):
        """ Get messages from specific broadcast """

        self.get_object()
        filters = self.get_filters(request)

        queryset = models.Message.objects \
            .filter(broadcast_id=pk) \
            .select_related('author', 'deleter') \
            .order_by('-created')

        if len(filters):
            queryset = queryset.filter(**filters)

        return self.list_response(queryset)
