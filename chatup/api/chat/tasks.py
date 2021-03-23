from django.conf import settings
from django.core.cache import cache
from django.db.models import F

from config import app
from . import models, serializers


@app.task
def update_watch_time() -> None:
    """ Update users watchtime in an active broadcast """

    broadcast = models.Broadcast.objects.filter(is_active=True).only('is_active').first()
    if not broadcast:
        return
    watchers = tuple(broadcast.watchers.keys())
    if not watchers:
        return
    delta = settings.USERS_WATCH_TIME_DELTA
    models.User.objects.filter(id__in=watchers).update(watchtime=F('watchtime') + delta)


@app.task
def cache_images() -> None:
    """ Cache images list with configured timeout """

    serializer = serializers.ImageCacheSerializer(models.Image.objects.all(), many=True)
    cache.set(models.Image.list_key(), serializer.data, timeout=None)
