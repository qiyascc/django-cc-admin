###############
# Qiyas Sadıqov CC
###############

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django_app = get_asgi_application()

try:
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter

    from cc_admin.routing import websocket_urlpatterns

    application = ProtocolTypeRouter({"http": django_app, "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns))})
except ImportError:
    application = django_app
