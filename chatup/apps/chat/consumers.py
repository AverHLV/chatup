from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    Async chat consumer that creates message instances in the database
    and sends them to other room members
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None

    async def connect(self) -> None:
        """ Enter room on connecting """

        self.room_name = f"chat_{self.scope['url_route']['kwargs']['name']}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code) -> None:
        """ Leave room on disconnect """

        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive_json(self, content, **kwargs) -> None:
        if not isinstance(content, dict):
            await self.send_json({'message': 'Invalid content'})
            return

        event = {'type': 'chat_message', 'message': content['message']}
        await self.channel_layer.group_send(self.room_name, event)

    async def chat_message(self, event: dict) -> None:
        """ Send a message to the user if received """

        await self.send_json({'message': event['message']})
