from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()), # Route for the chat WebSocket
   re_path(r'ws/inbox/$', consumers.InboxConsumer.as_asgi()),
]
