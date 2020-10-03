from rest_framework import mixins, viewsets
from rest_framework.views import APIView, Response

from . import models, serializers


class UserView(APIView):
    """ Get current user info """

    @staticmethod
    def get(request):
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data)


class RoleViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ User roles viewset """

    queryset = models.Role.objects.order_by('sid')
    serializer_class = serializers.RoleSerializer
