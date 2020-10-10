import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    """ Basic chat consumer """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None

    def connect(self) -> None:
        """ Enter room on connecting """

        self.room_name = f"chat_{self.scope['url_route']['kwargs']['name']}"
        async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)
        self.accept()

    def disconnect(self, code) -> None:
        """ Leave room on disconnect """

        async_to_sync(self.channel_layer.group_discard)(self.room_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None) -> None:
        try:
            received_data = json.loads(text_data)

        except (TypeError, json.JSONDecodeError):
            self.send(text_data=json.dumps({'message': 'Failed to deserialize data'}))
            return

        message = {'type': 'chat_message', 'message': received_data['message']}
        async_to_sync(self.channel_layer.group_send)(self.room_name, message)

    def chat_message(self, event: dict) -> None:
        """ Send a message to the user if received """

        self.send(text_data=json.dumps({'message': event['message']}))
