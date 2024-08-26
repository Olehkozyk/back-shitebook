from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Chat, Message
from channels.db import database_sync_to_async
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2
import base64
import os
from dotenv import load_dotenv

load_dotenv()


def generate_secret_key():
    password = os.getenv('AES_PASSWORD').encode('utf-8')
    salt = os.getenv('AES_SALT').encode('utf-8')
    key = PBKDF2(password, salt, dkLen=32)
    return key


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        self.room_name = None
        self.secret_key = generate_secret_key()

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['id']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        messages = await self.get_chat_history(self.room_name)
        for message in messages:
            await self.send(text_data=json.dumps({
                'message': message['content'],
                'user': message['sender'],
                'timestamp': message['timestamp']
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def save_message(self, chat_id, sender, content):
        chat = Chat.objects.get(id=chat_id)
        encrypted_content = self.encrypt_message(content)
        message = Message.objects.create(chat=chat, sender=sender, content=encrypted_content)
        return message.timestamp

    @database_sync_to_async
    def get_chat_history(self, chat_id):
        chat = Chat.objects.get(id=chat_id)
        messages = chat.messages.order_by('timestamp').values('sender__username', 'content', 'timestamp')
        return [{'sender': message['sender__username'], 'content': self.decrypt_message(message['content']), 'timestamp': message['timestamp'].isoformat()} for message in messages]

    def encrypt_message(self, message):
        cipher = AES.new(self.secret_key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')

    def decrypt_message(self, encrypted_message):
        encrypted_message = base64.b64decode(encrypted_message)
        nonce = encrypted_message[:16]
        tag = encrypted_message[16:32]
        ciphertext = encrypted_message[32:]
        cipher = AES.new(self.secret_key, AES.MODE_EAX, nonce=nonce)
        decrypted_message = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_message.decode('utf-8')

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']

        if user.is_authenticated:
            timestamp = await self.save_message(self.room_name, user, message)
        else:
            timestamp = None

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.username if user.is_authenticated else 'Anonymous',
                'timestamp': timestamp.isoformat() if timestamp else ''
            }
        )

    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        timestamp = event.get('timestamp', '')

        await self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'timestamp': timestamp
        }))