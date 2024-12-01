from django.urls import re_path

from chat import views

websocket_urlpatterns = [
    re_path("ws/chat/", views.ChatConsumer.as_asgi()),
]
