from django.urls import re_path

import chat.views


websocket_urlpatterns = [
	re_path(r'^ws/chat/(?P<app_name>[^/]+)/$', chat.views.train.as_asgi()),
    re_path('ws/test_train_page1_audio/', chat.views.test_train_page1_audio.as_asgi()),
]
