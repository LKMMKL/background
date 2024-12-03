from django.urls import re_path

from chat import views

websocket_urlpatterns = [
    re_path("ws/chat/", views.ChatConsumer.as_asgi()),
    re_path('ws/test_train_page1_audio/', views.test_train_page1_audio.as_asgi()),
]
