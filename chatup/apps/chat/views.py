from rest_framework import mixins, viewsets
from rest_framework.views import APIView, Response

from drf_yasg.utils import swagger_auto_schema

from . import models, serializers


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
