###############
# Qiyas Sadıqov CC
###############

import importlib.util
import io
import json
import unittest
from unittest import mock

from asgiref.sync import async_to_sync
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from cc_admin import live, notify, themes
from cc_admin.models import Notification, PushSubscription
from shop.models import Customer, Order, Product

RULES = {
    "NOTIFICATIONS": {
        "rules": [
            {"model": "shop.order", "on": "created", "title": "New order {obj.number}", "level": "success", "sound": "cash"},
            {"model": "shop.order", "on": "updated", "when": "shop.notifications.refunded", "title": "{obj.number} refunded", "to": "superuser", "level": "danger"},
        ]
    }
}


class NotificationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", orders=40, verbosity=0)
        User = get_user_model()
        cls.admin = User.objects.get(username="admin")
        cls.member = User.objects.get(username="murad")
        cls.outsider = User.objects.create_user("guest", password="guest")

    def setUp(self):
        Notification.objects.all().delete()
        self.client.force_login(self.admin)

    def test_recipients(self):
        staff = set(notify.recipients("staff").values_list("username", flat=True))
        self.assertIn("murad", staff)
        self.assertNotIn("guest", staff)
        self.assertEqual(list(notify.recipients("superuser").values_list("username", flat=True)), ["admin"])
        self.assertIn("murad", set(notify.recipients("group:Store team").values_list("username", flat=True)))
        self.assertEqual(list(notify.recipients("user:leyla").values_list("username", flat=True)), ["leyla"])
        self.assertIn("murad", set(notify.recipients("perm:shop.change_order").values_list("username", flat=True)))
        self.assertEqual(set(notify.recipients(["superuser", "user:leyla"]).values_list("username", flat=True)), {"admin", "leyla"})

    def test_notify_and_exclude_actor(self):
        made = notify.notify("staff", "Hello", body="World", actor=self.admin, exclude_actor=True)
        self.assertTrue(made)
        self.assertFalse(Notification.objects.filter(recipient=self.admin).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.member, title="Hello").exists())

    @override_settings(CC_ADMIN=RULES)
    def test_model_rules(self):
        order = Order.objects.create(number="NW-1", customer=Customer.objects.first(), total=10)
        self.assertTrue(Notification.objects.filter(recipient=self.member, title="New order NW-1", sound="cash").exists())
        order = Order.objects.get(pk=order.pk)
        order.status = "refunded"
        order.save()
        refunds = Notification.objects.filter(title="NW-1 refunded")
        self.assertEqual(list(refunds.values_list("recipient__username", flat=True)), ["admin"])
        order = Order.objects.get(pk=order.pk)
        order.save()
        self.assertEqual(Notification.objects.filter(title="NW-1 refunded").count(), 1)

    def test_poll_returns_new_notifications(self):
        url = reverse("admin:cc_live")
        first = self.client.get(url).json()
        self.assertEqual(first["since"], 0)
        notify.notify(self.admin, "Ping", level="warning", icon="package")
        data = self.client.get(url, {"since": first["since"]}).json()
        self.assertEqual([n["title"] for n in data["notifications"]], ["Ping"])
        self.assertIn("<symbol", data["notifications"][0]["svg"])
        self.assertEqual(data["unread"], 1)
        response = self.client.post(reverse("admin:cc_notifications_read"), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.json()["unread"], 0)

    def test_bell_page_and_json(self):
        notify.notify(self.admin, "One")
        self.assertEqual(self.client.get(reverse("admin:cc_notifications"), {"format": "json"}).json()["items"][0]["title"], "One")
        self.assertContains(self.client.get(reverse("admin:cc_notifications")), "cc-ntf")
        self.assertContains(self.client.get(reverse("admin:index")), "data-bell")

    def test_broadcast(self):
        response = self.client.post(reverse("admin:cc_notifications_send"), {"to": "group:Store team", "title": "Team meeting", "level": "info"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Notification.objects.filter(title="Team meeting").count(), 5)
        self.client.force_login(self.member)
        self.assertEqual(self.client.get(reverse("admin:cc_notifications_send")).status_code, 403)

    def test_settings_off(self):
        with self.settings(CC_ADMIN={"NOTIFICATIONS": False, "LIVE": False}):
            response = self.client.get(reverse("admin:index"))
            self.assertNotContains(response, "data-bell")
            self.assertNotContains(response, "data-live-dot")
            self.assertEqual(self.client.get(reverse("admin:cc_live")).status_code, 403)
            self.assertEqual(notify.notify("staff", "x"), [])


class LiveTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", orders=30, verbosity=0)
        User = get_user_model()
        cls.admin = User.objects.get(username="admin")
        cls.member = User.objects.get(username="leyla")

    def setUp(self):
        self.client.force_login(self.admin)

    def test_versions_change(self):
        before = live.versions(["shop.order", "*"])
        live._tops.clear()
        Order.objects.create(number="NW-2", customer=Customer.objects.first(), total=5)
        live._tops.clear()
        after = live.versions(["shop.order", "*"])
        self.assertNotEqual(before["shop.order"], after["shop.order"])
        self.assertNotEqual(before["*"], after["*"])

    def test_list_and_form_markers(self):
        self.assertContains(self.client.get(reverse("admin:shop_order_changelist")), "data-live-model")
        order = Order.objects.first()
        self.assertContains(self.client.get(reverse("admin:shop_order_change", args=[order.pk])), "data-live-object")
        self.assertContains(self.client.get(reverse("admin:index")), "data-live-dashboard")

    def test_object_changed_and_presence(self):
        order = Order.objects.first()
        key = f"shop.order:{order.pk}:{live.object_log('shop.order', order.pk)}"
        url = reverse("admin:cc_live")
        self.client.force_login(self.member)
        self.client.get(url, {"object": key, "mode": "editing"})
        LogEntry.objects.create(user=self.member, content_type=ContentType.objects.get_for_model(Order), object_id=str(order.pk), object_repr=str(order), action_flag=CHANGE, change_message=json.dumps([{"changed": {"fields": ["Status"]}}]))
        self.client.force_login(self.admin)
        data = self.client.get(url, {"object": key}).json()
        self.assertEqual(data["object"]["who"], "Leyla Karimova")
        self.assertIn("Status", data["object"]["message"])
        self.assertEqual(data["presence"][0]["mode"], "editing")

    def test_badges(self):
        data = self.client.get(reverse("admin:cc_live"), {"badges": "1"}).json()
        self.assertIn("nav:/admin/shop/order/", data["badges"])

    @override_settings(CC_ADMIN={"LIVE": {"stream_seconds": 1, "interval": 1}})
    def test_stream(self):
        response = self.client.get(reverse("admin:cc_live_stream"), {"since": 0, "models": "shop.order=x"})
        self.assertEqual(response["Content-Type"], "text/event-stream")
        chunks = []
        for chunk in response.streaming_content:
            chunks.append(chunk.decode() if isinstance(chunk, bytes) else chunk)
            if len(chunks) > 3:
                break
        frame = next(c for c in chunks if c.startswith("data: "))
        self.assertIn("shop.order", json.loads(frame[6:])["versions"])


PUSH = {"PUSH": {"enabled": True, "vapid_public_key": "BPublicKey", "vapid_private_key": "private", "vapid_claims": {"sub": "mailto:a@b.c"}}}


class PushTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser("boss", "boss@example.com", "boss")

    def setUp(self):
        self.client.force_login(self.user)

    def test_service_worker(self):
        response = self.client.get(reverse("admin:cc_service_worker"))
        self.assertEqual(response["Service-Worker-Allowed"], reverse("admin:index"))
        self.assertIn(b"showNotification", response.content)

    @unittest.skipUnless(importlib.util.find_spec("pywebpush"), "pywebpush is not installed")
    @override_settings(CC_ADMIN=PUSH)
    def test_subscribe_and_send(self):
        body = {"endpoint": "https://push.example.com/abc", "keys": {"p256dh": "key", "auth": "secret"}}
        response = self.client.post(reverse("admin:cc_push_subscribe"), json.dumps(body), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PushSubscription.objects.count(), 1)
        with mock.patch("pywebpush.webpush") as webpush:
            note = notify.notify(self.user, "Pushed", push=False)[0]
            self.assertEqual(notify.send_push([self.user.pk], note), 1)
            payload = json.loads(webpush.call_args.kwargs["data"])
            self.assertEqual(payload["title"], "Pushed")
        response = self.client.post(reverse("admin:cc_push_unsubscribe"), json.dumps({"endpoint": body["endpoint"]}), content_type="application/json")
        self.assertEqual(PushSubscription.objects.count(), 0)
        config = json.loads(self.client.get(reverse("admin:index")).context["cc"]["client"])
        self.assertEqual(config["push"]["key"], "BPublicKey")

    def test_push_off_refuses(self):
        response = self.client.post(reverse("admin:cc_push_subscribe"), "{}", content_type="application/json")
        self.assertEqual(response.status_code, 403)

    @unittest.skipUnless(importlib.util.find_spec("cryptography"), "cryptography is not installed")
    def test_vapid_command(self):
        out = io.StringIO()
        call_command("cc_admin_vapid", stdout=out)
        self.assertIn("vapid_public_key", out.getvalue())


@unittest.skipUnless(importlib.util.find_spec("channels") and importlib.util.find_spec("daphne"), "channels is not installed")
@override_settings(CC_ADMIN={"LIVE": {"transport": "websocket"}}, CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
class SocketTest(TransactionTestCase):
    def test_sync_and_poke(self):
        from channels.testing import WebsocketCommunicator

        from cc_admin.consumers import LiveConsumer

        user = get_user_model().objects.create_superuser("socket", "s@example.com", "socket")

        async def run():
            communicator = WebsocketCommunicator(LiveConsumer.as_asgi(), "/ws/cc-admin/")
            communicator.scope["user"] = user
            connected, _ = await communicator.connect()
            self.assertTrue(connected)
            await communicator.send_json_to({"type": "sync", "params": {"since": 0}})
            reply = await communicator.receive_json_from(timeout=5)
            self.assertEqual(reply["type"], "sync")
            self.assertIn("unread", reply["data"])
            from channels.layers import get_channel_layer

            await get_channel_layer().group_send(f"cc_admin_user_{user.pk}", {"type": "cc.poke"})
            self.assertEqual((await communicator.receive_json_from(timeout=5))["type"], "poke")
            await communicator.disconnect()

        async_to_sync(run)()

    def test_anonymous_is_refused(self):
        from channels.testing import WebsocketCommunicator
        from django.contrib.auth.models import AnonymousUser

        from cc_admin.consumers import LiveConsumer

        async def run():
            communicator = WebsocketCommunicator(LiveConsumer.as_asgi(), "/ws/cc-admin/")
            communicator.scope["user"] = AnonymousUser()
            connected, _ = await communicator.connect()
            self.assertFalse(connected)

        async_to_sync(run)()


class ThemeSettingsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser("theme", "t@example.com", "theme")

    def setUp(self):
        self.client.force_login(self.user)

    @override_settings(CC_ADMIN={"THEME": "nord", "THEMES": {"nord": {"label": "Fjord", "colors": {"accent": "#ff0055", "dark": {"accent": "#ff88aa"}}, "fonts": {"body": "Manrope"}, "radius": "round", "scheme": "dark", "layout": "topbar"}, "classic": {"enabled": False}}, "THEME_ORDER": ["nord", "cc"]})
    def test_builtin_overrides(self):
        registry = themes.registry()
        self.assertNotIn("classic", registry)
        self.assertEqual(list(registry)[:2], ["nord", "cc"])
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, 'data-theme="nord"')
        self.assertContains(response, 'data-scheme="dark"')
        self.assertContains(response, 'data-layout="topbar"')
        self.assertContains(response, "html.cc[data-skin=nord]{--cc-accent:#ff0055")
        self.assertContains(response, '--cc-font:"Manrope"')
        self.assertContains(response, "html.cc[data-skin=nord][data-scheme=dark]{--cc-accent:#ff88aa")
        self.assertContains(response, "Fjord")

    @override_settings(CC_ADMIN={"ANNOUNCEMENTS": [{"id": "a", "title": "Hello all", "style": "modal"}, {"id": "b", "title": "Old news", "end": "2000-01-01"}, {"id": "c", "title": "Bosses only", "permission": "none"}]})
    def test_announcements(self):
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, "Hello all")
        self.assertNotContains(response, "Old news")
        self.assertNotContains(response, "Bosses only")
