from django.db.models import F
from django.db.transaction import atomic
from django.utils.translation import gettext as _

from channels import exceptions
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from . import models, serializers


class EventTypes:
    """ Allowed event types container """

    # input types

    CREATE_MESSAGE = 'create_message'
    DELETE_MESSAGE = 'delete_message'
    UPDATE_WATCH_TIME = 'update_watch_time'

    # other

    ERROR = 'error'
    SEND_MESSAGE = 'send_message'
    CLOSE_BROADCAST = 'close_broadcast'
    UPDATE_WATCHERS_COUNT = 'update_watchers_count'

    _types = (
        CREATE_MESSAGE,
        DELETE_MESSAGE,
        UPDATE_WATCH_TIME,
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
    @atomic
    def get_broadcast(self):
        """
        Get broadcast by url parameter, reject connection if not found,
        else increase watchers count

        :raises: DenyConnection
        """

        try:
            broadcast = models.Broadcast.objects \
                .select_related('streamer') \
                .select_for_update() \
                .get(id=self.scope['url_route']['kwargs']['id'], is_active=True)

        except models.Broadcast.DoesNotExist:
            raise exceptions.DenyConnection('Broadcast not found')

        else:
            broadcast.watchers_count += 1
            broadcast.save(update_fields=['watchers_count'])
            return broadcast

    @database_sync_to_async
    @atomic
    def leave_broadcast(self):
        """ Leave broadcast on disconnecting by decreasing watchers count """

        self.scope['broadcast'].watchers_count = models.Broadcast.objects \
            .select_for_update() \
            .filter(id=self.scope['broadcast'].id) \
            .update(watchers_count=F('watchers_count') - 1)

    async def send_watchers_count_update(self) -> None:
        """ Send event in case of broadcast watchers count update """

        event = {
            'type': self.event_types.UPDATE_WATCHERS_COUNT,
            'content': {'watchers_count': self.scope['broadcast'].watchers_count},
        }

        await self.channel_layer.group_send(self.broadcast_id, event)

    async def connect(self) -> None:
        """ Enter room on connect """

        self.broadcast_id = str(self.scope['url_route']['kwargs']['id'])
        await self.channel_layer.group_add(self.broadcast_id, self.channel_name)

        self.check_user()
        self.scope['broadcast'] = await self.get_broadcast()

        await self.send_watchers_count_update()
        await self.accept()

    async def disconnect(self, code) -> None:
        """ Leave room on disconnect """

        if 'broadcast' in self.scope:
            await self.leave_broadcast()
            await self.send_watchers_count_update()

        await self.channel_layer.group_discard(self.broadcast_id, self.channel_name)

    async def receive_json(self, message, **kwargs) -> None:
        """ Received messages entrypoint. Perform actions based on a message type """

        if not await self.is_valid(message):
            return

        if message['type'] == self.event_types.CREATE_MESSAGE:
            await self.create_message(message['content'])

    async def is_valid(self, message: dict) -> bool:
        """ Validate basic structure of received WS message """

        response = None

        if not isinstance(message, dict) or 'type' not in message or 'content' not in message:
            response = {'type': self.event_types.ERROR, 'content': _('Invalid message structure.')}

        elif message['type'] not in self.event_types:
            response = {'type': self.event_types.ERROR, 'content':  _('Invalid message type.')}

        if response is None:
            return True

        await self.send_json(response)
        return False

    async def create_message(self, content: dict) -> None:
        """ 'create_message' type handler """

        message, errors = await self._create_message(content)

        if errors is not None:
            await self.send_json({'type': self.event_types.ERROR, 'content': errors})
            return

        event = {'type': self.event_types.SEND_MESSAGE, 'content': message}
        await self.channel_layer.group_send(self.broadcast_id, event)

    @database_sync_to_async
    def _create_message(self, content: dict) -> tuple:
        """
        Validate message content and return a tuple with newly created object
        or validation errors
        """

        content['author'] = self.scope['user'].id
        content['broadcast'] = self.scope['broadcast'].id
        serializer = serializers.MessageSerializer(data=content, context={'request': self.scope})

        if not serializer.is_valid():
            return None, serializer.errors

        serializer.save()
        return serializer.data, None

    async def send_message(self, event: dict) -> None:
        """ Group event handler: send a message to the user """

        await self.send_json(event)

    async def update_watchers_count(self, event: dict) -> None:
        """ Group event handler: send new 'watchers_count' value """

        await self.send_json(event)
