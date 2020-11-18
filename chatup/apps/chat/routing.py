from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'api/ws/rooms/(?P<id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
