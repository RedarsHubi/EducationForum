import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from app.views import update_unread_count
from app.models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    # In-memory list to store the last 20 messages
    recent_messages = []

    async def connect(self):
        self.room_name = "chat_room"
        self.room_group_name = f'chat_{self.room_name}'
        self.channel_layer = get_channel_layer()

        # Join the chat room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

        # Send the recent messages to the client
        for message in self.recent_messages:
            await self.send(text_data=json.dumps({
                'user': message['user'],
                'message': message['message'],
            }))

    async def disconnect(self, close_code):
        # Remove the user from the chat room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope['user']
        message = data.get('message')

        # Save the chat message in memory
        self.save_chat_message(user.name, message)

        # Broadcast the chat message to the chat room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': user.name,
                'message': message,
            }
        )

    async def chat_message(self, event):
        # Send the message to the client
        await self.send(text_data=json.dumps({
            'user': event['user'],
            'message': event['message'],
        }))

    def save_chat_message(self, user, message):
        # Save the new message to the in-memory list
        self.recent_messages.append({'user': user, 'message': message})

        # Keep only the last 20 messages
        if len(self.recent_messages) > 20:
            self.recent_messages.pop(0)

class InboxConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f'inbox_{self.user.id}'

        # Join the user's inbox group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the user's inbox group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_id = text_data_json['message_id']

        # Handle the received message (e.g., mark as read, update unread count)
        await self.handle_message(message_id)

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        Message.objects.filter(id=message_id).update(is_read=True)

    @database_sync_to_async
    def get_unread_count(self):
        return Message.objects.filter(receiver=self.user, is_read=False).count()

    async def handle_message(self, message_id):
        # Mark the message as read
        await self.mark_message_as_read(message_id)

        # Update the unread message count and notify other connected clients
        unread_count = await self.get_unread_count()
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'unread_count_update',
                'unread_count': unread_count
            }
        )

    async def unread_count_update(self, event):
        unread_count = event['unread_count']
        await self.send(text_data=json.dumps({
            'type': 'unread_count_update',
            'unread_count': unread_count
        }))
