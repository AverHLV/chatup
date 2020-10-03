from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _

from ..abstract import NameTranslation

ROLE_SIDS = (
    ('user', 'User'),
    ('moderator', 'Moderator'),
    ('administrator', 'Administrator'),
    ('streamer', 'Streamer'),
)

USER_ROLE_SID = ROLE_SIDS[0][0]
MODER_ROLE_SID = ROLE_SIDS[1][0]
ADMIN_ROLE_SID = ROLE_SIDS[2][0]
STREAMER_ROLE_SID = ROLE_SIDS[3][0]

USER_DEFAULT_ROLE_ID = 1


class Role(NameTranslation):
    """
    User role model, defines user permissions

    name: user-friendly multi-language sid representation
    sid: role string identifier
    """

    sid = models.CharField(max_length=20, unique=True, choices=ROLE_SIDS)

    class Meta:
        db_table = 'roles'
        verbose_name = _('role')
        verbose_name_plural = _('roles')

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
    watchtime: total time of the watched broadcasts (seconds)
    username_color: username color in chat, hex format, black by default
    role: user-specific role, ordinary users have 'user' role by default
    """

    email = models.EmailField(unique=True, blank=True, null=True)

    watchtime = models.PositiveIntegerField(
        default=0,
        help_text=_('Total time of the watched broadcasts (seconds).')
    )

    username_color = models.CharField(
        default='000000',
        max_length=6,
        validators=[validators.RegexValidator(r'^(?:[0-9a-fA-F]{3}){2}$')],
        help_text=_('Username color in chat, hex format.')
    )

    role = models.ForeignKey(
        Role,
        verbose_name=_('role'),
        default=USER_DEFAULT_ROLE_ID,
        on_delete=models.PROTECT,
        related_name='users'
    )

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f'{self.pk}: {self.username}'
