from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
        read_only_fields = 'id', 'watchtime', 'role'


class UserPublicSerializer(UserSerializer):
    class Meta:
        model = models.CustomUser
        fields = USER_PUBLIC_FIELDS


class BroadcastSerializer(serializers.ModelSerializer):
    streamer = UserPublicSerializer(read_only=True)

    class Meta:
        model = models.Broadcast
        exclude = 'watchers',

    def validate_is_active(self, value: bool) -> bool:
        """ Allow only one active broadcast per streamer """

        if value:
            active = models.Broadcast.objects \
                .filter(streamer=self.context['request'].user, is_active=True) \
                .exists()
            if active:
                raise ValidationError({'is_active': _('You can have only one active broadcast.')})

        return value

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.context is None:
            return

        # ws case

        if isinstance(self.context['request'], dict):
            self.fields['author'] = serializers.PrimaryKeyRelatedField(
                queryset=models.CustomUser.objects.only('id')
            )

            self.fields['deleter'] = serializers.PrimaryKeyRelatedField(
                required=False,
                queryset=models.CustomUser.objects.only('id')
            )

    @staticmethod
    def get_is_deleted(obj) -> bool:
        return obj.is_deleted

    def validate(self, attrs: dict) -> dict:
        # restore fields in ws case

        if self.context is not None and isinstance(self.context['request'], dict):
            self.fields['author'] = UserPublicSerializer()
            self.fields['deleter'] = UserPublicSerializer()

        return attrs
