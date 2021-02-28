import os

from django import setup
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

setup()
application = get_default_application()
