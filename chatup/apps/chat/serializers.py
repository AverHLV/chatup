from rest_framework import serializers

from . import models
from ..serializers import TranslatedModelSerializer

USER_PUBLIC_FIELDS = 'id', 'username', 'watchtime', 'username_color', 'role'
USER_FIELDS = USER_PUBLIC_FIELDS + ('email',)


class RoleSerializer(TranslatedModelSerializer):
    class Meta:
        model = models.Role
        fields = 'id', 'sid', 'name'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = USER_FIELDS


class UserPublicSerializer(UserSerializer):
    class Meta:
        model = models.CustomUser
        fields = USER_PUBLIC_FIELDS


class BroadcastSerializer(serializers.ModelSerializer):
    streamer = UserPublicSerializer(read_only=True)

    class Meta:
        model = models.Broadcast
        fields = '__all__'

    def validate(self, attr: dict) -> dict:
        request = self.context['request']

        if request.method == 'POST':
            attr['streamer'] = request.user

        return attr


class MessageSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer()
    deleter = UserPublicSerializer()
    is_deleted = serializers.SerializerMethodField()

    class Meta:
        model = models.Message
        fields = '__all__'

    @staticmethod
    def get_is_deleted(obj) -> bool:
        return obj.is_deleted
