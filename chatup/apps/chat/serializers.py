from rest_framework import serializers

from . import models
from ..serializers import TranslatedModelSerializer


class RoleSerializer(TranslatedModelSerializer):
    class Meta:
        model = models.Role
        fields = 'id', 'sid', 'name'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = 'id', 'username', 'email', 'watchtime', 'username_color', 'role'
