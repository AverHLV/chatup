import re

from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.db.models import Q

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS

from api.abstract.serializers import TranslatedModelSerializer, BinaryImageField
from . import models, tasks

UPDATE_METHODS = 'PUT', 'PATCH'
USER_PUBLIC_FIELDS = 'id', 'username', 'watchtime', 'username_color', 'role', 'role_icon'
USER_FIELDS = USER_PUBLIC_FIELDS + ('email',)


class RoleSerializer(TranslatedModelSerializer):
    class Meta:
        model = models.Role
        fields = 'id', 'sid', 'name'


class UserPublicSerializer(serializers.ModelSerializer):
    role_icon = serializers.IntegerField(source='icon', read_only=True)

    class Meta:
        model = models.User
        fields = USER_PUBLIC_FIELDS


class UserSerializer(serializers.ModelSerializer):
    role_icon = serializers.IntegerField(source='icon', read_only=True)

    class Meta:
        model = models.User
        fields = USER_FIELDS
        read_only_fields = 'id', 'watchtime', 'role'


class UserControlSerializer(UserSerializer):
    """ User management by higher powers """

    class Meta(UserSerializer.Meta):
        fields = USER_PUBLIC_FIELDS + ('custom_images',)
        read_only_fields = 'id', 'username', 'username_color', 'watchtime'
        extra_kwargs = {
            'role': {'queryset': models.Role.objects.only('sid')},
            'custom_images': {'queryset': models.Image.objects.filter(type=models.Image.TYPES.CUSTOM).only('type')},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_icon_old_field = None

    def is_valid(self, raise_exception=False):
        request = self.context['request']
        if request.method not in SAFE_METHODS and 'role_icon' in request.data:
            self.role_icon_old_field = self.fields['role_icon']
            try:
                int(request.data['role_icon'])
            except (ValueError, TypeError, OverflowError):
                custom_size = models.Image.SIZES[models.Image.TYPES.CUSTOM]
                self.fields['role_icon'] = BinaryImageField(size=custom_size)
            else:
                self.fields['role_icon'] = serializers.PrimaryKeyRelatedField(
                    allow_null=True,
                    queryset=models.Image.objects.only('id'),
                )

        return super().is_valid(raise_exception)

    def validate_role(self, value):
        request = self.context['request']
        if request.user.id == self.instance.id and value.id != self.instance.role_id:
            raise ValidationError({'role': _('You cannot change role of yourself.')})

        return value

    @staticmethod
    def validate_custom_images(value):
        if {models.Image.TYPES.CUSTOM} != {icon.type for icon in value}:
            raise ValidationError({'custom_images': _('Custom images must be of type custom.')})

        return value

    @transaction.atomic
    def save(self, **kwargs):
        if isinstance(self.fields['role_icon'], BinaryImageField):
            # role_icon is passed as base64
            self.validated_data['role_icon'] = models.Image.objects.create(
                image=self.validated_data['role_icon'],
                type=models.Image.TYPES.CUSTOM,
            )

        return super().save(**kwargs)

    def to_representation(self, instance):
        if self.role_icon_old_field:
            self.fields['role_icon'] = self.role_icon_old_field

        return super().to_representation(instance)


class ImageCacheSerializer(serializers.ModelSerializer):
    image = BinaryImageField()

    class Meta:
        model = models.Image
        fields = 'id', 'image', 'type', 'description', 'role'
        extra_kwargs = {'role': {'queryset': models.Role.objects.only('sid')}}


class ImageSerializer(ImageCacheSerializer):
    class Meta(ImageCacheSerializer.Meta):
        fields = ImageCacheSerializer.Meta.fields + ('users',)
        extra_kwargs = {
            'role': {'queryset': models.Role.objects.only('sid')},
            'users': {'source': 'custom_owners', 'required': False, 'queryset': models.User.objects.only('username')}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context['request']
        user_role = getattr(request.user, 'role', None)

        if request.method in UPDATE_METHODS:
            self.fields['type'].read_only = True
        elif (
                request.method in SAFE_METHODS
                and (not user_role or user_role.sid not in {models.Role.SIDS.ADMIN, models.Role.SIDS.STREAMER})
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

    def is_valid(self, raise_exception=False):
        image_type = self.context['request'].data.get('type')
        if image_type and isinstance(image_type, str):
            self.fields['image'].size = models.Image.SIZES.get(image_type)
        return super().is_valid(raise_exception)

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        tasks.cache_images.delay()
        return instance


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
    is_deleted = serializers.BooleanField(read_only=True)
    author = UserPublicSerializer()
    deleter = UserPublicSerializer()

    class Meta:
        model = models.Message
        fields = '__all__'


class MessageWSSerializer(MessageSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=models.User.objects.only('id'))
    deleter = serializers.PrimaryKeyRelatedField(required=False, queryset=models.User.objects.only('id'))
    regex_image = re.compile(r"{{ image\|\d+ }}")

    def validate(self, attrs: dict) -> dict:
        posted_images = {int(image[9:-3]) for image in self.regex_image.findall(attrs['text'])}
        if posted_images:
            available_images = models.Image.objects \
                .filter(Q(custom_owners=attrs['author'].id) |
                        Q(type=models.Image.TYPES.SMILEY, role_id=attrs['author'].role_id)) \
                .values_list('pk', flat=True)
            prohibited_images = posted_images - set(available_images)
            if prohibited_images:
                prohibited_ids_list = ", ".join(str(image_id) for image_id in prohibited_images)
                raise ValidationError({
                    'text': _("Images not found: %(images)s") % {"images": prohibited_ids_list}
                })

        self.fields['author'] = UserPublicSerializer()
        self.fields['deleter'] = UserPublicSerializer()

        return attrs


class MessageUpdateWSSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    deleter_id = serializers.IntegerField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)
