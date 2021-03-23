import os

from django.conf import settings
from celery import Celery

from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery(__file__)
app.config_from_object(settings, namespace='CELERY')
app.conf.beat_schedule = {
    'update-watch-time': {
        'task': 'api.chat.tasks.update_watch_time',
        'schedule': timedelta(seconds=settings.USERS_WATCH_TIME_DELTA),
    },
}
app.autodiscover_tasks()
