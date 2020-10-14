from channels import exceptions
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from . import models


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    Async chat consumer that creates message instances in the database
    and sends them to other room members
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.broadcast_id: str = None

    def check_user(self) -> None:
        """
        Check whether user is authenticated

        :raises: DenyConnection
        """

        if not self.scope['user'].is_authenticated:
            raise exceptions.DenyConnection('User is not authenticated')

    @database_sync_to_async
    def get_broadcast(self):
        """
        Get broadcast by url parameter, reject connection if not found

        :raises: DenyConnection
        """

        try:
            return models.Broadcast.objects \
                .select_related('streamer') \
                .get(id=self.scope['url_route']['kwargs']['id'], is_active=True)

        except models.Broadcast.DoesNotExist:
            raise exceptions.DenyConnection('Broadcast not found')

    async def connect(self) -> None:
        """ Enter room on connect """

        self.broadcast_id = str(self.scope['url_route']['kwargs']['id'])
        await self.channel_layer.group_add(self.broadcast_id, self.channel_name)

        self.check_user()
        self.scope['broadcast'] = await self.get_broadcast()

        await self.accept()

    async def disconnect(self, code) -> None:
        """ Leave room on disconnect """

        await self.channel_layer.group_discard(self.broadcast_id, self.channel_name)

    async def receive_json(self, content, **kwargs) -> None:
        if not isinstance(content, dict):
            await self.send_json({'message': 'Invalid content'})
            return

        event = {'type': 'chat_message', 'message': content['message']}
        await self.channel_layer.group_send(self.broadcast_id, event)

    async def chat_message(self, event: dict) -> None:
        """ Send a message to the user if received """

        await self.send_json({'message': event['message']})
