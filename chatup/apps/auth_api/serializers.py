from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=User._meta.get_field(User.USERNAME_FIELD).max_length
    )

    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        max_length=User._meta.get_field('password').max_length
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None

    def validate(self, attrs: dict) -> dict:
        """ Find user instance by the given credentials """

        self.user = authenticate(self.context['request'], **attrs)

        if self.user is None:
            raise ValidationError({'detail': _('User not found by the given credentials.')})

        return attrs
