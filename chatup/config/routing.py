import apps.chat.routing as chat_routing

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

router = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            *chat_routing.websocket_urlpatterns,
        ])
    ),
})
