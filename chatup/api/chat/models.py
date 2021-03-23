from django.db import models
from django.core import validators
from django.core.cache import cache
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _

from redis.exceptions import RedisError
from model_utils import Choices

from api.abstract.models import TimeStamped, NameTranslation


class Image(models.Model):
    TYPES = Choices(
        ('smiley', 'SMILEY', 'Smiley'),
        ('icon', 'ICON', 'Icon'),
        ('badge', 'BADGE', 'Badge'),
        ('custom', 'CUSTOM', 'Custom'),
    )

    SIZES = {
        TYPES.SMILEY: (28, 28),
        TYPES.ICON: (18, 18),
        TYPES.BADGE: (18, 18),
        TYPES.CUSTOM: (30, 30),
    }

    image = models.BinaryField()
    type = models.CharField(choices=TYPES, max_length=30)
    description = models.CharField(blank=True, null=True, max_length=300)
    role = models.ForeignKey('Role', null=True, on_delete=models.CASCADE, related_name='images')

    class Meta:
        db_table = 'images'

    def __str__(self):
        return f'{self.pk}: {self.type}'

    @classmethod
    def list_key(cls) -> str:
        """ Redis key for Image list response """

        return 'IMAGE_LIST'


class RoleQuerySet(models.QuerySet):
    def prefetch_icon(self, to_attr: str = 'icon'):
        prefetch = models.Prefetch('images', queryset=Image.objects.filter(type=Image.TYPES.ICON), to_attr=to_attr)
        return self.prefetch_related(prefetch)

    def prefetch_smiles(self, to_attr: str = 'smiles'):
        prefetch = models.Prefetch('images', queryset=Image.objects.filter(type=Image.TYPES.SMILEY), to_attr=to_attr)
        return self.prefetch_related(prefetch)


class Role(NameTranslation):
    """
    User role model, defines user permissions

    name: user-friendly multi-language sid representation
    sid: role string identifier
    """

    SIDS = Choices(
        ('user', 'USER', 'User'),
        ('vip', 'VIP', 'VIP'),
        ('moderator', 'MODERATOR', 'Moderator'),
        ('administrator', 'ADMINISTRATOR', 'Administrator'),
        ('streamer', 'STREAMER', 'Streamer'),
    )

    sid = models.CharField(max_length=20, unique=True, choices=SIDS)

    objects = RoleQuerySet.as_manager()

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

    role_icon = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)
    custom_images = models.ManyToManyField(Image, related_name='custom_owners')

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f'{self.pk}: {self.username}'

    @property
    def icon(self) -> (int, None):
        return self.role_icon_id or self.role.images.filter(type=Image.TYPES.ICON).values_list('id', flat=True).first()


class Broadcast(TimeStamped):
    """
    User broadcast model

    title: broadcast title
    description: broadcast description
    is_active: whether broadcast is active now, False by default
    source_link: absolute url to the broadcast source
    streamer: user who is streaming
    """

    title = models.CharField(unique=True, max_length=200)
    description = models.CharField(blank=True, null=True, max_length=1000)
    is_active = models.BooleanField(default=False, help_text=_('Whether broadcast is active now.'))
    source_link = models.URLField(verbose_name=_('source link'), help_text=_('Link to broadcast source.'))

    streamer = models.ForeignKey(
        User,
        verbose_name=_('streamer'),
        on_delete=models.PROTECT,
        related_name='broadcasts'
    )

    class Meta:
        db_table = 'broadcasts'
        verbose_name = _('broadcast')
        verbose_name_plural = _('broadcasts')
        indexes = models.Index(fields=['created', 'is_active']),

    def __str__(self):
        return f'{self.pk}: {self.title[:20]}'

    @property
    def watchers_key(self) -> str:
        """ Retrieve broadcast watchers key for Redis """

        return f'BROADCAST_{self.id}_WATCHERS'

    @property
    def watchers_lock_key(self) -> str:
        """ Retrieve broadcast watchers lock key for Redis """

        return f'BROADCAST_{self.id}_WATCHERS_LOCK'

    @property
    def watchers(self) -> dict:
        """
        Retrieve watchers dictionary in format:
            watcher_id: devices count
        """

        return cache.get(self.watchers_key, {}) if self.is_active else {}

    @property
    def watchers_count(self) -> int:
        return len(self.watchers)

    def change_watcher(self, watcher_id: int, add: bool = True) -> tuple:
        """
        Add or remove watcher in an active broadcast

        :param watcher_id: user id
        :param add: whether to add or delete given watcher
        :return: distinct watchers count, whether to send an event (bool, None)
        """

        if not self.is_active:
            return 0, False

        send_event = False
        lock = cache.lock(self.watchers_lock_key, thread_local=False)
        lock.acquire()

        try:
            watchers = self.watchers
            if watcher_id in watchers:
                if add:
                    watchers[watcher_id] += 1
                elif watchers[watcher_id] > 1:
                    watchers[watcher_id] -= 1
                else:
                    watchers.pop(watcher_id)
                    send_event = True
            elif add:
                watchers[watcher_id] = 1
                send_event = True
            else:
                return len(watchers), None

            cache.set(self.watchers_key, watchers, timeout=None)
            return len(watchers), send_event
        except RedisError:
            return 0, False
        finally:
            lock.release()

    def clear_watchers(self) -> None:
        """ Remove watchers data for this broadcast """

        cache.delete(self.watchers_key)


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
        return f'{self.pk}: {self.text[:20]}'

    @property
    def is_deleted(self) -> bool:
        """ Check whether this message is deleted """

        return self.deleter_id is not None
