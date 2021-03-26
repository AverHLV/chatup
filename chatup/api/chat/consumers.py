from django.db.models import F
from django.utils.translation import gettext as _

from channels import exceptions
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from asgiref.sync import async_to_sync
from model_utils import Choices

from . import models, serializers

channel_layer = get_channel_layer()


class ChatSyncSenderMixin:
    """ Mixin for sending chat events from sync environment """

    @classmethod
    def send_broadcast_update(cls, broadcast_id: int, data: dict) -> None:
        event = {
            'type': cls.EVENT_TYPES.UPDATE_BROADCAST,
            'content': data,
        }
        async_to_sync(channel_layer.group_send)(str(broadcast_id), event)

    @classmethod
    def send_close_broadcast_update(cls, broadcast_id: int) -> None:
        event = {
            'type': cls.EVENT_TYPES.CLOSE_BROADCAST,
            'content': {},
        }
        async_to_sync(channel_layer.group_send)(str(broadcast_id), event)


class ChatConsumer(ChatSyncSenderMixin, AsyncJsonWebsocketConsumer):
    """
    Async chat consumer that creates message instances in the database
    and sends them to other room members
    """

    CLOSE_BROADCAST_CODE = 4001

    EVENT_TYPES = Choices(
        ('send_message', 'SEND_MESSAGE', 'Send message'),
        ('create_message', 'CREATE_MESSAGE', 'Create message'),
        ('update_message', 'UPDATE_MESSAGE', 'Update message'),
        ('delete_message', 'DELETE_MESSAGE', 'Delete message'),
        ('undo_delete_message', 'UNDO_DELETE_MESSAGE', 'Undo delete message'),
        ('error', 'ERROR', 'Error'),
        ('close_broadcast', 'CLOSE_BROADCAST', 'Close broadcast'),
        ('update_broadcast', 'UPDATE_BROADCAST', 'Update broadcast'),
        ('update_watchers_count', 'UPDATE_WATCHERS_COUNT', 'Update watchers count'),
    )

    INPUT_EVENT_TYPES = {
        EVENT_TYPES.CREATE_MESSAGE,
        EVENT_TYPES.DELETE_MESSAGE,
        EVENT_TYPES.UNDO_DELETE_MESSAGE,
    }

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
    def get_broadcast(self) -> tuple:
        """
        Get broadcast and watchers count by url parameter, reject connection if not found
        else add current user as a watcher

        :return: broadcast, watchers count, whether to sent event (bool, None)
        :raises: DenyConnection
        """

        broadcast = models.Broadcast.objects.filter(id=int(self.broadcast_id), is_active=True).first()
        if not broadcast:
            raise exceptions.DenyConnection('Broadcast not found')
        return (broadcast, *broadcast.change_watcher(self.scope['user'].id))

    @database_sync_to_async
    def leave_broadcast(self):
        """
        Leave broadcast on disconnecting by removing current user from watchers,
        returns broadcast and watchers count

        :return: broadcast, watchers count, whether to sent event (bool, None)
        """

        broadcast = self.scope['broadcast']
        return (broadcast, *broadcast.change_watcher(self.scope['user'].id, add=False))

    async def connect(self) -> None:
        """ Enter room on connect """

        self.broadcast_id = str(self.scope['url_route']['kwargs']['id'])
        await self.channel_layer.group_add(self.broadcast_id, self.channel_name)

        self.check_user()
        self.scope['broadcast'], watchers_count, send_to_group = await self.get_broadcast()

        await self.accept()
        await self.send_watchers_count_update(watchers_count, send_to_group)

    async def disconnect(self, code) -> None:
        """ Leave room on disconnect """

        if 'broadcast' in self.scope:
            self.scope['broadcast'], watchers_count, send_to_group = await self.leave_broadcast()
            await self.send_watchers_count_update(watchers_count, send_to_group)

        await self.channel_layer.group_discard(self.broadcast_id, self.channel_name)

    async def receive_json(self, event, **kwargs) -> None:
        """ Received client events entrypoint. Perform actions based on an event type """

        if not await self.is_valid(event):
            return

        event_type = event['type']
        content = event['content']

        if event_type == self.EVENT_TYPES.CREATE_MESSAGE:
            await self.create_message(content)
        elif event_type == self.EVENT_TYPES.DELETE_MESSAGE:
            await self.handle_message_update(content, True)
        elif event_type == self.EVENT_TYPES.UNDO_DELETE_MESSAGE:
            await self.handle_message_update(content, False)

    async def is_valid(self, event: dict) -> bool:
        """ Validate basic structure of received event """

        response = None

        if not isinstance(event, dict) or 'type' not in event or 'content' not in event:
            response = {'type': self.EVENT_TYPES.ERROR, 'content': _('Invalid event structure.')}
        elif event['type'] not in self.INPUT_EVENT_TYPES:
            response = {'type': self.EVENT_TYPES.ERROR, 'content':  _('Invalid event type.')}

        if not response:
            return True

        await self.send_json(response)
        return False

    async def send_watchers_count_update(
            self,
            watchers_count: (int, None),
            send_to_group: bool
    ) -> None:
        """
        Send event in case of broadcast watchers count update

        :param watchers_count: count of broadcast watchers, return immediately if None
        :param send_to_group: whether to send watchers count update event to a group
        """

        if watchers_count is None:
            return

        event = {
            'type': self.EVENT_TYPES.UPDATE_WATCHERS_COUNT,
            'content': {'watchers_count': watchers_count},
        }
        if send_to_group:
            await self.channel_layer.group_send(self.broadcast_id, event)
        else:
            await self.update_watchers_count(event)

    async def create_message(self, content: dict) -> None:
        """ 'create_message' type handler """

        message, errors = await self._create_message(content)
        if errors:
            await self.send_json({'type': self.EVENT_TYPES.ERROR, 'content': errors})
            return

        event = {'type': self.EVENT_TYPES.SEND_MESSAGE, 'content': message}
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

    async def handle_message_update(self, content: dict, is_delete: bool) -> None:
        """ Handle DELETE_MESSAGE or UNDO_DELETE_MESSAGE input events """

        response = None
        allowed_roles = {models.Role.SIDS.MODER, models.Role.SIDS.ADMIN, models.Role.SIDS.STREAMER}
        if self.scope['user'].role.sid not in allowed_roles:
            response = {
                'type': self.EVENT_TYPES.ERROR,
                'content': _('You do not have permission to perform this action.'),
            }
        serializer = serializers.MessageUpdateWSSerializer(data=content)
        if not serializer.is_valid():
            response = {'type': self.EVENT_TYPES.ERROR, 'content': serializer.errors}

        if response:
            await self.send_json(response)
            return

        message = await self.get_message(content['id'], is_delete)
        if not message:
            await self.send_json({'type': self.EVENT_TYPES.ERROR, 'content': _('Not found.')})
            return

        if not self.check_message_permissions(message, is_delete):
            await self.send_json({
                'type': self.EVENT_TYPES.ERROR,
                'content': _('You do not have permission to perform this action.'),
            })
            return

        await self._update_message(message, is_delete)
        serializer = serializers.MessageUpdateWSSerializer(message)
        event = {
            'type': self.EVENT_TYPES.UPDATE_MESSAGE,
            'content': serializer.data,
        }
        await self.channel_layer.group_send(self.broadcast_id, event)

    @database_sync_to_async
    def get_message(self, message_id: int, is_delete: bool):
        message = models.Message.objects.filter(id=message_id)
        if is_delete:
            message = message.filter(deleter_id__isnull=True).annotate(author_sid=F('author__role__sid'))
        else:
            message = message.filter(deleter_id__isnull=False).annotate(deleter_sid=F('deleter__role__sid'))
        return message.first()

    @database_sync_to_async
    def _update_message(self, message, is_delete: bool) -> None:
        if is_delete:
            message.mark_as_deleted(self.scope['user'].id)
        else:
            message.undo_mark_as_deleted()

    def check_message_permissions(self, message, is_delete: bool) -> bool:
        """ Check user permissions during DELETE_MESSAGE or UNDO_DELETE_MESSAGE events """

        user_sid = self.scope['user'].role.sid

        if is_delete:
            allowed_sids_for_moder = models.Role.SIDS.USER, models.Role.SIDS.VIP
            allowed_sids_for_admin = allowed_sids_for_moder + (models.Role.SIDS.MODER,)
            allowed_sids_for_streamer = allowed_sids_for_admin + ( models.Role.SIDS.ADMIN,)

            if (
                message.author_id == self.scope['user'].id
                or (user_sid == models.Role.SIDS.MODER and message.author_sid in allowed_sids_for_moder)
                or (user_sid == models.Role.SIDS.ADMIN and message.author_sid in allowed_sids_for_admin)
                or (user_sid == models.Role.SIDS.STREAMER and message.author_sid in allowed_sids_for_streamer)
            ):
                return True

        else:
            allowed_sids_for_streamer = {models.Role.SIDS.MODER, models.Role.SIDS.ADMIN}

            if (
                message.deleter_id == self.scope['user'].id
                or (user_sid == models.Role.SIDS.ADMIN and message.deleter_sid == models.Role.SIDS.MODER)
                or (user_sid == models.Role.SIDS.STREAMER and message.deleter_sid in allowed_sids_for_streamer)
            ):
                return True

        return False

    async def send_message(self, event: dict) -> None:
        """ Group event handler: send a message to the user """

        await self.send_json(event)

    async def update_message(self, event: dict) -> None:
        """ Group event handler: send new message data """

        await self.send_json(event)

    async def update_watchers_count(self, event: dict) -> None:
        """ Group event handler: send new 'watchers_count' value """

        await self.send_json(event)

    async def update_broadcast(self, event: dict) -> None:
        """ Group event handler: send new broadcast data """

        await self.send_json(event)

    async def close_broadcast(self, _event: dict) -> None:
        """
        Discard group and close connection with special code from the server end
        if broadcast is no more active

        :raises: StopConsumer
        """

        await self.channel_layer.group_discard(self.broadcast_id, self.channel_name)
        await self.close(self.CLOSE_BROADCAST_CODE)
        raise exceptions.StopConsumer()
