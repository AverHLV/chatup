from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS

from api.abstract.serializers import TranslatedModelSerializer, BinaryImageField
from . import models

UPDATE_METHODS = 'PUT', 'PATCH'
USER_PUBLIC_FIELDS = 'id', 'username', 'watchtime', 'username_color', 'role'
USER_FIELDS = USER_PUBLIC_FIELDS + ('email',)


class RoleSerializer(TranslatedModelSerializer):
    class Meta:
        model = models.Role
        fields = 'id', 'sid', 'name'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = USER_FIELDS
        read_only_fields = 'id', 'watchtime', 'role'


class CustomBinaryImageField(BinaryImageField):
    """
    In-memory image objects are resized based on image type
    and serialized into binary data.
    """

    def to_internal_value(self, data, **kwargs):
        image_type = self.context['request'].data['type']
        image_size = models.Image.SIZES[image_type]

        return super(CustomBinaryImageField, self).to_internal_value(data, resize=image_size)


class ImageSerializer(serializers.ModelSerializer):
    image = CustomBinaryImageField()

    class Meta:
        model = models.Image
        fields = 'id', 'image', 'type', 'description', 'role', 'users'
        extra_kwargs = {'users': {'source': 'custom_owners', 'required': False}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context['request']
        user_role = getattr(request.user, 'role', None)

        if request.method in UPDATE_METHODS:
            self.fields['type'].read_only = True
        elif (
            request.method in SAFE_METHODS
            and (not user_role or user_role.sid not in {models.Role.SIDS.ADMINISTRATOR, models.Role.SIDS.STREAMER})
        ):
            self.fields.pop('users')

    def validate(self, attrs):
        image_type = attrs.get('type') or self.instance.type
        is_custom = image_type == models.Image.TYPES.CUSTOM
        is_role_related = image_type in {models.Image.TYPES.ICON, models.Image.TYPES.SMILEY}

        if self.context['request'].method in UPDATE_METHODS:
            if not is_custom:
                attrs.pop('users', None)
            if not is_role_related:
                attrs.pop('role', None)
            else:
                role = attrs.get('role')
                if role and self.check_icon(image_type, role.id):
                    raise ValidationError({'type': _('You can have only one icon per role.')})

        else:
            if is_custom and not attrs.get('users'):
                raise ValidationError({'users': _('This field is required.')})
            elif not is_custom:
                attrs.pop('users', None)

            if not is_role_related:
                attrs.pop('role', None)
            else:
                role = attrs.get('role')
                if not role:
                    raise ValidationError({'role': _('This field is required.')})

                if self.check_icon(image_type, role.id):
                    raise ValidationError({'type': _('You can have only one icon per role.')})

        return attrs

    @staticmethod
    def check_icon(image_type: str, role_id: int) -> bool:
        if image_type != models.Image.TYPES.ICON:
            return False

        return models.Image.objects.filter(type=image_type, role_id=role_id).exists()


class UserPublicSerializer(UserSerializer):
    class Meta:
        model = models.User
        fields = USER_PUBLIC_FIELDS


class BroadcastSerializer(serializers.ModelSerializer):
    streamer = UserPublicSerializer(read_only=True)

    class Meta:
        model = models.Broadcast
        fields = '__all__'

    def validate_is_active(self, value: bool) -> bool:
        """ Allow only one active broadcast per streamer """

        if value:
            user = self.context['request'].user
            active = models.Broadcast.objects.filter(streamer_id=user.id, is_active=True).exists()
            if active:
                raise ValidationError({'is_active': _('You can have only one active broadcast.')})

        return value

    def validate(self, attrs: dict) -> dict:
        request = self.context['request']
        if request.method == 'POST':
            attrs['streamer'] = request.user
        return attrs

    def update(self, instance, validated_data: dict):
        """ Update broadcast, send ws events if needed """

        from .consumers import ChatConsumer

        closed = instance.is_active and not validated_data.get('is_active', True)
        updated = validated_data and tuple(validated_data.keys()) != ('is_active',)
        instance = super().update(instance, validated_data)

        if closed:
            ChatConsumer.send_close_broadcast_update(instance.id)
            instance.clear_watchers()
        elif updated:
            ChatConsumer.send_broadcast_update(instance.id, validated_data)

        return instance


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
                queryset=models.User.objects.only('id')
            )

            self.fields['deleter'] = serializers.PrimaryKeyRelatedField(
                required=False,
                queryset=models.User.objects.only('id')
            )

    @staticmethod
    def get_is_deleted(obj) -> bool:
        return obj.is_deleted

    def validate(self, attrs: dict) -> dict:
        # restore fields in ws case

        if self.context and isinstance(self.context['request'], dict):
            self.fields['author'] = UserPublicSerializer()
            self.fields['deleter'] = UserPublicSerializer()

        return attrs
