from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _

from model_utils import Choices

from api.abstract.models import TimeStamped, NameTranslation

IMAGE_TYPES = (
    ('smiley', 'Smiley'),
    ('role', 'Role'),
    ('experience', 'Experience'),
    ('status', 'Status'),
    ('event', 'Event'),
)

ROLE_ICONS = {
    'user': 1,
    'vip': 2,
    'moderator': 3,
    'administrator': 4,
    'streamer': 5
}


class Role(NameTranslation):
    """
    User role model, defines user permissions

    name: user-friendly multi-language sid representation
    sid: role string identifier
    """

    SIDS = Choices(
        ('user', 'User'),
        ('vip', 'VIP'),
        ('moderator', 'Moderator'),
        ('administrator', 'Administrator'),
        ('streamer', 'Streamer'),
    )

    sid = models.CharField(max_length=20, unique=True, choices=SIDS)

    class Meta:
        db_table = 'roles'
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def __str__(self):
        return self.sid


class Image(models.Model):
    """
    Image model

    exclusive_access_role: permanent access for specified role
    """

    image = models.BinaryField(blank=True, null=True, editable=True)
    type = models.CharField(choices=IMAGE_TYPES, max_length=20)
    description = models.CharField(blank=True, null=True, max_length=1000)
    exclusive_access_role = models.CharField(choices=Role.SIDS, null=True, max_length=20)

    class Meta:
        db_table = 'images'

    def __str__(self):
        return self.description


class CustomUserManager(UserManager):
    """ Custom manager for user fields eager loading """

    def get(self, *args, **kwargs):
        """ Load most needed related user fields (mainly for 'request.user') """

        return super().select_related('role').get(*args, **kwargs)


class User(AbstractUser):
    """
    email: user email for notifications or news, optional
    watchtime: total time of the watched broadcasts (seconds)
    username_color: username color in chat, hex format, black by default
    role: user-specific role, ordinary users have 'user' role by default
    """

    DEFAULT_ROLE_ID = 1

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
        default=DEFAULT_ROLE_ID,
        on_delete=models.PROTECT,
        related_name='users'
    )

    role_icon = models.ForeignKey(
        Image,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    available_images = models.ManyToManyField(
        Image,
        related_name="owners"
    )

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f'{self.pk}: {self.username}'

    def save(self, *args, **kwargs):
        if not self.role_icon:
            self.role_icon = Image.objects.get(pk=ROLE_ICONS[str(self.role)])

        super().save(*args, **kwargs)

        self.available_images.set(Image.objects.filter(exclusive_access_role=self.role.sid))


class Broadcast(TimeStamped):
    """
    User broadcast model

    title: broadcast title
    description: broadcast description
    is_active: whether broadcast is active now, False by default
    source_link: absolute url to the broadcast source
    streamer: user who is streaming
    watchers: users that watch the broadcast
    """

    title = models.CharField(unique=True, max_length=200)
    description = models.CharField(blank=True, null=True, max_length=1000)
    is_active = models.BooleanField(default=False, help_text=_('Whether broadcast is active now.'))

    source_link = models.URLField(
        verbose_name=_('source link'),
        help_text=_('Link to broadcast source.')
    )

    streamer = models.ForeignKey(
        User,
        verbose_name=_('streamer'),
        on_delete=models.PROTECT,
        related_name='broadcasts'
    )

    watchers = models.ManyToManyField(
        User,
        through='BroadcastToUser',
        verbose_name=_('watchers')
    )

    class Meta:
        db_table = 'broadcasts'
        verbose_name = _('broadcast')
        verbose_name_plural = _('broadcasts')
        indexes = models.Index(fields=['created']),

    def __str__(self):
        return self.title[:20]


class BroadcastToUser(models.Model):
    """ Custom many-to-many model that allows multiple relationships """

    broadcast = models.ForeignKey(Broadcast, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        db_table = 'broadcasts_to_users'


class Message(TimeStamped):
    """
    Chat message model

    text: message text
    broadcast: broadcast that this message belongs to
    author: user that added this message
    deleter: user that deleted this message, empty by default
    """

    text = models.CharField(max_length=500)

    broadcast = models.ForeignKey(
        Broadcast,
        verbose_name=_('broadcast'),
        on_delete=models.CASCADE,
        related_name='messages'
    )

    author = models.ForeignKey(
        User,
        verbose_name=_('author'),
        on_delete=models.PROTECT,
        related_name='messages'
    )

    deleter = models.ForeignKey(
        User,
        blank=True,
        null=True,
        verbose_name=_('deleter'),
        on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'messages'
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        indexes = models.Index(fields=['created']),

    def __str__(self):
        return self.text[:20]

    @property
    def is_deleted(self) -> bool:
        """ Check whether this message is deleted """

        return self.deleter_id is not None
