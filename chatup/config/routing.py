from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from chatup.apps.chat.routing import websocket_urlpatterns as chat_patterns

router = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            *chat_patterns,
        ])
    ),
})
