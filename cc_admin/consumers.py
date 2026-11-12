###############
# Qiyas Sadıqov CC
###############

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.http import QueryDict

from . import live


class SocketRequest:
    def __init__(self, scope):
        self.user = scope.get("user")
        self.GET = QueryDict()
        self.META = {}
        self.path = scope.get("path", "/")
        self.scope = scope

    def get_full_path(self):
        return self.path


class LiveConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated or not user.is_active or not user.is_staff or not live.settings().get("enabled"):
            await self.close(code=4403)
            return
        self.joined = ["cc_admin_all", f"cc_admin_user_{user.pk}"]
        if self.channel_layer is not None:
            for group in self.joined:
                await self.channel_layer.group_add(group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if self.channel_layer is not None:
            for group in getattr(self, "joined", []):
                await self.channel_layer.group_discard(group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") != "sync":
            return
        params = {str(k): str(v) for k, v in (content.get("params") or {}).items()}
        data = await database_sync_to_async(live.collect)(SocketRequest(self.scope), params)
        await self.send_json({"type": "sync", "data": data})

    async def cc_poke(self, event):
        await self.send_json({"type": "poke"})
