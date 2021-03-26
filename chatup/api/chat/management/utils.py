from django.conf import settings
from django.core.management.base import CommandError

from uuid import uuid4
from random import choice

from .. import models


def debug_required(handler) -> callable:
    """
    Check debug mode decorator

    :raises: CommandError
    """

    def wrapper(*args, **kwargs):
        if not settings.DEBUG:
            raise CommandError('This command allowed only in debug mode')

        return handler(*args, **kwargs)

    return wrapper


def create_broadcasts(count: int) -> tuple:
    """ Create broadcasts with generated data, mark one as active if no active broadcasts """

    streamers = models.User.objects.filter(role__sid=models.Role.SIDS.STREAMER)
    if not streamers:
        raise CommandError('No streamers in database')

    broadcasts = [
        models.Broadcast(title=f'Stream #{uuid4()}', streamer=choice(streamers), is_active=False)
        for _ in range(count)
    ]
    models.Broadcast.objects.bulk_create(broadcasts)
    active_broadcast = None

    # mark one broadcast as active

    if not models.Broadcast.objects.filter(is_active=True).exists():
        active_broadcast = models.Broadcast.objects.first()
        active_broadcast.is_active = True
        active_broadcast.save(update_fields=['is_active'])

    return broadcasts, active_broadcast


def create_messages(count: int) -> list:
    broadcasts = models.Broadcast.objects.all()
    users = models.User.objects.all()
    moderators = models.User.objects.filter(role__sid=models.Role.SIDS.MODER)
    if not broadcasts or not users or not moderators:
        raise CommandError('No needed data in database')

    messages = [
        models.Message(
            text='Message text',
            broadcast=choice(broadcasts),
            author=choice(users),
            deleter=choice(moderators) if not i % 5 else None
        )
        for i in range(count)
    ]
    models.Message.objects.bulk_create(messages)
    return messages
