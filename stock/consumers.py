import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


class ItemConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.category_id = ""

    async def connect(self):
        self.category_id = self.scope['url_route']['kwargs']['category_id']

        # Join room group
        await self.channel_layer.group_add(
            self.category_id,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.category_id,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data, **kwargs):
        text_data_json = json.loads(text_data)
        item = text_data_json['item']

        # Send message to room group
        await self.channel_layer.group_send(
            self.category_id,
            {
                'type': 'item_created_message',
                'item': item
            }
        )

    # Receive message from room group
    async def item_created_message(self, event):
        item = event['item']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'item': item
        }))


def send_item_created_message(_category_id, item):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        str(_category_id),
        {
            'type': 'item_created_message',
            'item': {"price": item.price, "name": item.name, "uid": item.uid}
        }
    )
