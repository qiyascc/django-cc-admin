###############
# Qiyas Sadıqov CC
###############

import threading
import time
import zlib

from django.apps import apps
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Max
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.translation import gettext as _

from . import conf

PREFIX = "cc_admin:live:"


class Bus:
    def __init__(self):
        self.condition = threading.Condition()
        self.tick = 0

    def poke(self):
        with self.condition:
            self.tick += 1
            self.condition.notify_all()

    def wait(self, since, timeout):
        with self.condition:
            if self.tick == since:
                self.condition.wait(timeout)
            return self.tick


bus = Bus()


def settings():
    return conf.get("LIVE")


def enabled(request=None):
    data = settings()
    if not data.get("enabled"):
        return False
    if request is None:
        return True
    user = getattr(request, "user", None)
    return bool(user and user.is_authenticated and user.is_active and user.is_staff)


def _cache_get(key, default=None):
    try:
        return cache.get(PREFIX + key, default)
    except Exception:
        return default


def _cache_set(key, value, timeout=None):
    try:
        cache.set(PREFIX + key, value, timeout)
    except Exception:
        pass


def bump(label):
    key = f"v:{label}"
    try:
        if not cache.add(PREFIX + key, 1, None):
            cache.incr(PREFIX + key)
        if not cache.add(PREFIX + "v:*", 1, None):
            cache.incr(PREFIX + "v:*")
    except Exception:
        pass
    poke_all()


def poke_all():
    bus.poke()
    _channels_send("cc_admin_all", {"type": "cc.poke"})


def poke_users(ids):
    bus.poke()
    for pk in set(ids):
        _channels_send(f"cc_admin_user_{pk}", {"type": "cc.poke"})


def _channels_send(group, message):
    if settings().get("transport") != "websocket":
        return
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
    except ImportError:
        return
    layer = get_channel_layer()
    if layer is None:
        return
    try:
        async_to_sync(layer.group_send)(group, message)
    except Exception:
        pass


def _content_type(label):
    try:
        app_label, model = label.split(".")
        return ContentType.objects.get_by_natural_key(app_label, model)
    except (ValueError, ContentType.DoesNotExist):
        return None


_tops = {}


def table_top(label):
    hit = _tops.get(label)
    if hit and time.monotonic() - hit[0] < 2:
        return hit[1]
    model = model_from_label(label)
    value = 0
    if model is not None:
        try:
            value = model._default_manager.aggregate(m=Max("pk"))["m"] or 0
        except Exception:
            value = 0
    _tops[label] = (time.monotonic(), value)
    return value


def versions(labels):
    labels = [l for l in labels if l]
    if not labels:
        return {}
    found = {}
    if "*" in labels:
        top = LogEntry.objects.aggregate(m=Max("id"))["m"] or 0
        tables = zlib.crc32("|".join(f"{label}:{table_top(label)}" for label in sorted(_registered())).encode())
        found["*"] = f"{top}.{_cache_get('v:*', 0)}.{tables}"
    types = {}
    for label in labels:
        if label == "*":
            continue
        ct = _content_type(label)
        if ct is not None:
            types[ct.pk] = label
    logs = dict(LogEntry.objects.filter(content_type_id__in=list(types)).values("content_type_id").annotate(m=Max("id")).values_list("content_type_id", "m"))
    for pk, label in types.items():
        found[label] = f"{logs.get(pk) or 0}.{_cache_get('v:' + label, 0)}.{table_top(label)}"
    return found


def object_log(label, pk):
    ct = _content_type(label)
    if ct is None:
        return 0
    return LogEntry.objects.filter(content_type=ct, object_id=str(pk)).aggregate(m=Max("id"))["m"] or 0


def object_changes(request, label, pk, since):
    ct = _content_type(label)
    if ct is None:
        return None
    entry = (
        LogEntry.objects.filter(content_type=ct, object_id=str(pk), id__gt=since)
        .exclude(user_id=request.user.pk)
        .select_related("user")
        .order_by("-id")
        .first()
    )
    if entry is None:
        return None
    who = entry.user.get_full_name() or entry.user.get_username() if entry.user_id else ""
    return {
        "log": entry.pk,
        "who": who,
        "deleted": entry.is_deletion(),
        "message": entry.get_change_message() if entry.is_change() else "",
        "ago": _("just now") if (timezone.now() - entry.action_time).total_seconds() < 60 else _("%(time)s ago") % {"time": timesince(entry.action_time)},
    }


def presence(request, label, pk, mode):
    key = f"p:{label}:{pk}"
    now = time.time()
    ttl = max(30, int(settings().get("interval", 5)) * 4, int(settings().get("hidden_interval", 30)) * 2 + 10)
    data = dict(_cache_get(key, {}) or {})
    user = request.user
    data[str(user.pk)] = {
        "t": now,
        "mode": mode if mode in ("viewing", "editing") else "viewing",
        "name": user.get_full_name() or user.get_username(),
        "username": user.get_username(),
    }
    data = {k: v for k, v in data.items() if now - v.get("t", 0) < ttl}
    _cache_set(key, data, ttl)
    return [{"name": v["name"], "username": v["username"], "mode": v["mode"]} for k, v in sorted(data.items()) if k != str(user.pk)]


def leave(request, label, pk):
    key = f"p:{label}:{pk}"
    data = dict(_cache_get(key, {}) or {})
    data.pop(str(request.user.pk), None)
    _cache_set(key, data, 120)


def parse(params):
    models = {}
    for part in (params.get("models") or "").split(","):
        if not part:
            continue
        label, _, version = part.partition("=")
        models[label] = version
    obj = None
    raw = params.get("object") or ""
    if raw.count(":") >= 2:
        label, pk, log = raw.split(":", 2)
        try:
            obj = (label, pk, int(log or 0))
        except ValueError:
            obj = None
    try:
        since = int(params["since"]) if params.get("since") not in (None, "") else None
    except ValueError:
        since = None
    return {"models": models, "object": obj, "since": since, "mode": params.get("mode") or "viewing", "badges": params.get("badges") == "1"}


def collect(request, params):
    from . import navigation, notify

    state = parse(params)
    data = {"t": int(time.time())}
    notes = notify.unseen(request.user, state["since"])
    data["notifications"] = notes["items"]
    data["unread"] = notes["unread"]
    data["since"] = notes["since"]
    if state["models"]:
        current = versions(list(state["models"]))
        data["versions"] = current
    if state["object"] and settings().get("forms"):
        label, pk, log = state["object"]
        change = object_changes(request, label, pk, log)
        if change:
            data["object"] = change
        if settings().get("presence"):
            data["presence"] = presence(request, label, pk, state["mode"])
    if state["badges"] and settings().get("badges"):
        data["badges"] = navigation.badges(request)
    return data


def model_label(instance):
    opts = instance._meta
    return f"{opts.app_label}.{opts.model_name}"


def _registered():
    from django.contrib import admin

    return {f"{m._meta.app_label}.{m._meta.model_name}" for m in admin.site._registry if m._meta.app_label != "cc_admin"}


def on_change(sender, instance=None, **kwargs):
    if not settings().get("enabled"):
        return
    if sender is LogEntry:
        poke_all()
        return
    if sender._meta.app_label in ("sessions", "contenttypes", "cc_admin") or sender._meta.model_name == "logentry":
        return
    label = f"{sender._meta.app_label}.{sender._meta.model_name}"
    if label in _registered():
        bump(label)


def connect():
    from django.db.models.signals import post_delete, post_save

    post_save.connect(on_change, dispatch_uid="cc_admin_live_save")
    post_delete.connect(on_change, dispatch_uid="cc_admin_live_delete")


def model_from_label(label):
    try:
        return apps.get_model(label)
    except (LookupError, ValueError):
        return None
