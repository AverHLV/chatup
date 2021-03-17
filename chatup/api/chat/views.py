from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, viewsets, permissions, status
from rest_framework.views import APIView, Response
from rest_framework.decorators import action

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from itertools import groupby

from ..abstract.views import ModelViewSetBase
from . import models, serializers, permissions as own_permissions

User = get_user_model()

author_param = openapi.Parameter(
    'author_id',
    openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    description='Author filter'
)


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

    queryset = models.Broadcast.objects.select_related('streamer').order_by('-is_active', '-created')
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

        watchers = tuple(broadcast.watchers.keys())
        if not watchers:
            users = []
        else:
            users = User.objects.filter(id__in=watchers).annotate(role_sid=F('role__sid'))

        result = {
            key: self.get_serializer(group, many=True).data
            for key, group in groupby(users, key=lambda x: x.role_sid)
        }

        # reorder by role sids

        return Response({
            'result': {role: result[role] for role, __ in reversed(models.Role.SIDS) if role in result}
        })


class ImageViewSet(viewsets.ModelViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    permission_classes = own_permissions.IsStreamer,

    def list(self, request, *args, **kwargs):
        # don`t paginate queryset

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
