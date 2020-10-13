from django.conf import settings
from django.core.management.base import CommandError


def debug_required(handler) -> None:
    """
    Check debug mode decorator

    :raises: CommandError
    """

    def wrapper(*args, **kwargs):
        if not settings.DEBUG:
            raise CommandError('This command allowed only in debug mode')

        return handler(*args, **kwargs)

    return wrapper
