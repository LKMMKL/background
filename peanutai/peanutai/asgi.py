"""
WSGI config for peanutai project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.wsgi import get_wsgi_application
from . import routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peanutai.settings')

application = ProtocolTypeRouter({
    "http": get_wsgi_application(),
    "websocket": URLRouter(
            routing.websocket_urlpatterns
        )
})
