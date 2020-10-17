from django.utils.translation import gettext_lazy as _

from channels import exceptions
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from . import models, serializers


class EventTypes:
    """ Allowed input event types container """

    CREATE_MESSAGE = 'create_message'
    DELETE_MESSAGE = 'delete_message'
    UPDATE_WATCH_TIME = 'update_watch_time'
    UPDATE_WATCHERS_COUNT = 'update_watchers_count'

    _types = (
        CREATE_MESSAGE,
        DELETE_MESSAGE,
        UPDATE_WATCH_TIME,
        UPDATE_WATCHERS_COUNT,
    )

    def __contains__(self, item: str) -> bool:
        """
        Check that item is an allowed event type

        :raises: AssertionError
        """

        assert isinstance(item, str), 'Item should be a string'
        return item in self._types


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    Async chat consumer that creates message instances in the database
    and sends them to other room members
    """

    event_types = EventTypes()

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

    async def receive_json(self, message, **kwargs) -> None:
        """ Received messages entrypoint. Perform actions based on a message type """

        if not await self.is_valid(message):
            return

        if message['type'] == self.event_types.CREATE_MESSAGE:
            await self.create_message(message['content'])

    async def is_valid(self, message: dict) -> bool:
        """ Validate basic structure of received WS message """

        if not isinstance(message, dict) or 'type' not in message or 'content' not in message:
            await self.send_json({'type': 'error', 'content': _('Invalid message structure.')})
            return False

        if message['type'] not in self.event_types:
            await self.send_json({'type': 'error', 'content':  _('Invalid message type.')})
            return False

        return True

    async def create_message(self, content: dict) -> None:
        """ 'create_message' type handler """

        message, errors = await self._create_message(content)

        if errors is not None:
            await self.send_json({'type': 'error', 'content': errors})
            return

        event = {'type': 'send_message', 'content': message}
        await self.channel_layer.group_send(self.broadcast_id, event)

    @database_sync_to_async
    def _create_message(self, content: dict) -> tuple:
        """
        Validate message content and return a tuple with newly created object
        or validation errors
        """

        content['author'] = self.scope['user'].id
        content['broadcast'] = self.scope['broadcast'].id
        serializer = serializers.MessageWSSerializer(data=content, context={'request': self.scope})

        if not serializer.is_valid():
            return None, serializer.errors

        message = serializers.MessageSerializer(serializer.save()).data
        return message, None

    async def send_message(self, event: dict) -> None:
        """ Send a message to the user if received """

        await self.send_json(event)
