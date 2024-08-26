from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/chats/', ChatConsumer.as_asgi()),
    path('ws/chats/<int:id>/', ChatConsumer.as_asgi()),
]