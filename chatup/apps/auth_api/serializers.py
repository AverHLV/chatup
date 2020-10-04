from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()
USERNAME_LENGTH = User._meta.get_field(User.USERNAME_FIELD).max_length
PASSWORD_LENGTH = User._meta.get_field('password').max_length
EMAIL_LENGTH = User._meta.get_field('email').max_length


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = 'username', 'email'


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=USERNAME_LENGTH)
    password = serializers.CharField(required=True, max_length=PASSWORD_LENGTH)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None

    def validate(self, attrs: dict) -> dict:
        """ Find user instance by the given credentials """

        self.user = authenticate(self.context['request'], **attrs)

        if self.user is None:
            raise ValidationError({'detail': _('User not found by the given credentials.')})

        return attrs


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=USERNAME_LENGTH)
    password1 = serializers.CharField(required=True, max_length=PASSWORD_LENGTH)
    password2 = serializers.CharField(required=True, max_length=PASSWORD_LENGTH)
    email = serializers.EmailField(required=False, max_length=EMAIL_LENGTH)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.form = None

    def validate(self, attrs: dict) -> dict:
        """ Validate user data by the creation form """

        self.form = CustomUserCreationForm(data=attrs)

        if self.form.is_valid():
            return attrs

        rest_errors = {
            field: [error['message'] for error in errors]
            for field, errors in self.form.errors.get_json_data().items()
        }

        raise ValidationError(rest_errors)

    def create(self, validated_data: dict):
        """ Save new user instance """

        # exclude blank but not nullable emails

        if 'email' not in validated_data:
            self.form.instance.email = None

        return self.form.save()
