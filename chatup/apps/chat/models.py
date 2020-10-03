from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractUser, UserManager

from ..abstract import NameTranslation

ROLE_SIDS = (
    ('moderator', 'Moderator'),
    ('administrator', 'Administrator'),
    ('streamer', 'Streamer'),
)

MODER_ROLE_SID = ROLE_SIDS[0][0]
ADMIN_ROLE_SID = ROLE_SIDS[1][0]
STREAMER_ROLE_SID = ROLE_SIDS[2][0]


class Role(NameTranslation):
    """
    User role model, defines user privileges and permissions

    name: user-friendly multi-language sid representation
    sid: role string identifier
    """

    sid = models.CharField(max_length=20, unique=True, choices=ROLE_SIDS)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.sid


class CustomUserManager(UserManager):
    """ Custom manager for user fields eager loading """

    def get(self, *args, **kwargs):
        """ Load most needed related user fields (mainly for 'request.user') """

        return super().select_related('role').get(*args, **kwargs)


class CustomUser(AbstractUser):
    """
    Chatup custom user model

    email: user email for notifications or news, optional
    watched_time: total time of the watched broadcasts (seconds)
    nick_color: username color in the chat, black by default
    role: the user-specific role, ordinary users have no roles by default
    """

    email = models.EmailField(unique=True, blank=True, null=True)
    watched_time = models.PositiveIntegerField(default=0)

    nick_color = models.CharField(
        default='000000',
        max_length=6,
        validators=[validators.RegexValidator(r'^(?:[0-9a-fA-F]{3}){2}$')]
    )

    role = models.ForeignKey(
        Role,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='users'
    )

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.pk}: {self.username}'
