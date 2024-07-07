"""
ASGI config for education project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
"""
Defining the settings file path
"""
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'education.settings')

import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from education.routing import websocket_urlpatterns

"""
ProtocolTypeRouter: Routes incoming requests based on their protocol type (HTTP or WebSocket).
"""
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

# Note: Make sure to define websocket_urlpatterns in education/routing.py to specify WebSocket URL patterns.
