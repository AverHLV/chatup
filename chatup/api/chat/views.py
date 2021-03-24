from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db.models import F, Prefetch
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, viewsets, mixins, permissions, status
from rest_framework.views import APIView, Response
from rest_framework.decorators import action

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from itertools import groupby

from ..abstract.views import ModelViewSetBase
from . import models, serializers, tasks, permissions as own_permissions

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
    queryset = models.Role.objects.order_by('sid')
    serializer_class = serializers.RoleSerializer


class BroadcastViewSet(ModelViewSetBase):
    queryset = models.Broadcast.objects.order_by('-is_active', '-created')
    serializer_class = serializers.BroadcastSerializer
    permission_classes = own_permissions.IsStreamerOrReadOnly,
    filterset_fields = 'title', 'is_active', 'streamer_id'

    serializer_action_classes = {
        'messages': serializers.MessageSerializer,
        'watchers': serializers.UserPublicSerializer,
    }

    filterset_action_fields = {
        'messages': ('author_id',),
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset \
            .select_related('streamer') \
            .only(
                'created', 'updated', 'title', 'description', 'is_active', 'source_link', 'streamer__username',
                'streamer__username_color', 'streamer__watchtime', 'streamer__role_id'
            )

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
            .only(
                'created', 'updated', 'author_id', 'deleter_id', 'broadcast_id', 'text', 'author__username',
                'author__username_color', 'author__watchtime', 'author__role_id', 'deleter__username',
                'deleter__username_color', 'deleter__watchtime', 'deleter__role_id',
            ) \
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
            users = User.objects \
                .filter(id__in=watchers) \
                .annotate(role_sid=F('role__sid')) \
                .only('username', 'username_color', 'watchtime', 'role_id')

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
    permission_classes = permissions.IsAuthenticatedOrReadOnly, own_permissions.IsAdminStreamerOrReadOnly

    use_cache = True

    def get_queryset(self):
        queryset = super().get_queryset()
        if (
            self.request.user.is_authenticated
            and self.request.method in permissions.SAFE_METHODS
            and self.request.user.role.sid in {models.Role.SIDS.ADMIN, models.Role.SIDS.STREAMER}
        ):
            self.use_cache = False
            queryset = queryset.prefetch_related(Prefetch('custom_owners', queryset=User.objects.only('id')))
        return queryset

    def list(self, request, *args, **kwargs):
        # don`t paginate queryset, use cached response if needed

        queryset = self.filter_queryset(self.get_queryset())

        if self.use_cache:
            data = cache.get(models.Image.list_key(), None)
            if data is not None:
                return Response(data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        # send cache task on delete,
        # create and update cases will be handled by serializer

        super().perform_destroy(instance)
        tasks.cache_images.delay()


class UserControlViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.order_by('id')
    serializer_class = serializers.UserControlSerializer
    permission_classes = permissions.IsAuthenticated, own_permissions.IsStreamer
    filterset_fields = 'username',

    def get_queryset(self):
        queryset = super().get_queryset()
        custom_images = models.Image.objects.filter(type=models.Image.TYPES.CUSTOM).only('id')
        icon = models.Image.objects.filter(type=models.Image.TYPES.ICON).only('role_id')

        return queryset \
            .select_related('role') \
            .prefetch_related(
                Prefetch('custom_images', queryset=custom_images),
                Prefetch('role__images', queryset=icon, to_attr='icon'),
            ) \
            .only('username', 'username_color', 'watchtime', 'role_id', 'role_icon_id', 'role__sid')
