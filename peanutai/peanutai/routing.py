from django.urls import re_path

import chat.views


websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<app_name>[^/]+)/$', chat.views.ChatConsumer),
]