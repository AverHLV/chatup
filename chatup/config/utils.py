from django.conf import settings


def show_toolbar(_request) -> bool:
    """ Function to determine whether to show the debug toolbar """

    return settings.DEBUG
