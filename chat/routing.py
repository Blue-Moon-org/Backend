from django.urls import re_path
from .consumers import ChatConsumer, NewChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>[^/]+)/$', ChatConsumer.as_asgi()),
    re_path(r'^ws/chats/(?P<id>[^/]+)/$', NewChatConsumer.as_asgi()),
]