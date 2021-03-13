from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, viewsets, permissions, status
from rest_framework.views import APIView, Response
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from itertools import groupby
from operator import attrgetter

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
    filterset_action_fields: dict = {}

    def get_serializer_class(self):
        """ Look for serializer class in actions dictionary first """

        return self.serializer_action_classes.get(self.action) or super().get_serializer_class()

    def get_filters(self, request) -> dict:
        """ Build filters for custom actions """

        filters = {}

        for field in self.filterset_action_fields[self.action]:
            value = request.query_params.get(field, None)
            if value is not None:
                filters[field] = value

        return filters

    def list_response(self, queryset):
        """ List action for custom queryset """

        page = self.paginate_queryset(queryset)
        if page:
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

    @swagger_auto_schema(responses={'200': serializers.UserSerializer})
    def get(self, request):
        serializer = serializers.UserSerializer(
            request.user,
            context={'request': request, 'view': self}
        )

        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=serializers.UserSerializer,
        responses={'200': serializers.UserSerializer}
    )
    def patch(self, request):
        serializer = serializers.UserSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request, 'view': self}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class RoleView(generics.ListAPIView):
    """ User roles list view """

    queryset = models.Role.objects.order_by('sid')
    serializer_class = serializers.RoleSerializer


class BroadcastViewSet(ModelViewSetBase):
    """ User broadcasts viewset """

    queryset = models.Broadcast.objects.select_related('streamer').order_by('-created')
    serializer_class = serializers.BroadcastSerializer
    permission_classes = permissions.IsAuthenticatedOrReadOnly, own_permissions.IsBroadcastStreamer
    filterset_fields = 'title', 'is_active', 'streamer_id'

    serializer_action_classes = {
        'messages': serializers.MessageSerializer,
        'watchers': serializers.UserPublicSerializer,
    }

    filterset_action_fields = {
        'messages': ('author_id',),
    }

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active:
            return Response(
                {'detail': _('Only inactive broadcasts can be deleted.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

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

        if filters:
            queryset = queryset.filter(**filters)

        return self.list_response(queryset)

    @action(methods=['GET'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def watchers(self, request, pk):
        """ Get broadcast watchers, grouped by roles """

        broadcast = self.get_object()

        if not broadcast.is_active:
            return Response(
                {'detail': _('This broadcast is inactive.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        getter = attrgetter('role.sid')
        users = broadcast.watchers.select_related('role').distinct()

        result = {
            key: self.get_serializer(group, many=True).data
            for key, group in groupby(users, key=getter)
        }

        # reorder by role sids

        return Response({
            'result': {
                role: result[role] for role, __ in reversed(models.Role.SIDS) if role in result
            }
        })


class ImageViewSet(viewsets.ModelViewSet):
    """ Get images info """

    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    parser_classes = FormParser, MultiPartParser
    permission_classes = permissions.AllowAny,

    @swagger_auto_schema(
        request_body=serializers.ImageFieldSerializer,
        responses={'200': serializers.ImageSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data)
