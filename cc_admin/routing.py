###############
# Qiyas Sadıqov CC
###############

from django.urls import path

from . import conf
from .consumers import LiveConsumer

websocket_urlpatterns = [path(conf.get("LIVE").get("url", "/ws/cc-admin/").strip("/") + "/", LiveConsumer.as_asgi())]
