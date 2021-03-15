from django.conf import settings

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.abstract.serializers import TranslatedModelSerializer, BinaryImageField
from . import models

USER_PUBLIC_FIELDS = 'id', 'username', 'watchtime', 'username_color', 'role', 'role_icon'
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
        if self.context['request'].method in ['PUT', 'PATCH']:
            self.fields['type'].read_only = True

    def validate(self, attrs):
        image_type = attrs.get('type') or self.instance.type

        if image_type == models.Image.TYPES.CUSTOM:
            image_owners = attrs.get('custom_owners') or self.instance.custom_owners \
                if self.context['request'].method in ['PUT', 'PATCH'] \
                else attrs.get('custom_owners')
            if not image_owners:
                raise ValidationError({'users': _('Field is required for specified type.')})
        elif attrs.get('custom_owners'):
            raise ValidationError({'users': _('Field is not allowed for specified type.')})

        if image_type in [models.Image.TYPES.ICON, models.Image.TYPES.SMILEY]:
            role = attrs.get('role') or self.instance.role
            if not role:
                raise ValidationError({'role': _('Field role is required for specified type.')})

            if image_type == models.Image.TYPES.ICON:
                icon_exists = models.Image.objects.filter(type=image_type, role=role).exists()
                if icon_exists:
                    raise ValidationError({'type': _('You can have only one icon per role.')})

        return attrs


class UserPublicSerializer(UserSerializer):
    class Meta:
        model = models.User
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

    def validate(self, attrs: dict) -> dict:
        request = self.context['request']
        if request.method == 'POST':
            attrs['streamer'] = request.user
        return attrs


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

        if self.context is not None and isinstance(self.context['request'], dict):
            self.fields['author'] = UserPublicSerializer()
            self.fields['deleter'] = UserPublicSerializer()

        return attrs
