###############
# Qiyas Sadıqov CC
###############

import datetime
import json
import logging
import threading

from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet
from django.db.models.signals import post_delete, post_save
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from . import conf, current, icons, live
from .models import Notification, PushSubscription

log = logging.getLogger("cc_admin.notify")


def settings():
    return conf.get("NOTIFICATIONS")


def enabled():
    return bool(settings().get("enabled"))


def recipients(to, obj=None, actor=None):
    User = get_user_model()
    active = User.objects.filter(is_active=True)
    if to is None:
        return active.none()
    if callable(to) and not isinstance(to, (QuerySet, User)):
        return recipients(to(obj) if obj is not None else to(), None, actor)
    if isinstance(to, str) and conf.DOTTED.match(to):
        try:
            return recipients(conf.as_callable(to), obj, actor)
        except ImportError:
            return active.none()
    if isinstance(to, User):
        return active.filter(pk=to.pk)
    if isinstance(to, QuerySet):
        return to.filter(is_active=True)
    if isinstance(to, (list, tuple, set)):
        query = Q(pk__in=[])
        for item in to:
            query |= Q(pk__in=recipients(item, obj, actor).values("pk"))
        return active.filter(query)
    if isinstance(to, int):
        return active.filter(pk=to)
    if to in ("staff", "all", True):
        return active.filter(is_staff=True)
    if to == "superuser":
        return active.filter(is_superuser=True)
    if isinstance(to, str) and to.startswith("group:"):
        return active.filter(groups__name=to[6:]).distinct()
    if isinstance(to, str) and to.startswith("perm:"):
        app_label, codename = to[5:].split(".", 1)
        perm = Q(user_permissions__codename=codename, user_permissions__content_type__app_label=app_label)
        group = Q(groups__permissions__codename=codename, groups__permissions__content_type__app_label=app_label)
        return active.filter(Q(is_superuser=True) | (Q(is_staff=True) & (perm | group))).distinct()
    if isinstance(to, str) and to.startswith("user:"):
        return active.filter(**{User.USERNAME_FIELD: to[5:]})
    return active.none()


def notify(to, title, body="", link="", level="info", icon="", sound="", actor=None, key="", data=None, push=True, exclude_actor=False):
    if not enabled():
        return []
    users = recipients(to, actor=actor)
    if exclude_actor and actor is not None:
        users = users.exclude(pk=actor.pk)
    ids = list(users.values_list("pk", flat=True))
    if not ids:
        return []
    now = timezone.now()
    rows = [
        Notification(
            recipient_id=pk,
            actor=actor,
            title=str(title)[:200],
            body=str(body or ""),
            link=str(link or "")[:500],
            level=level if level in dict(Notification._meta.get_field("level").choices) else "info",
            icon=icon or "",
            sound=sound or "",
            key=str(key or "")[:120],
            data=data or {},
            created_at=now,
        )
        for pk in ids
    ]
    created = Notification.objects.bulk_create(rows)
    live.poke_users(ids)
    if push and conf.get("PUSH").get("enabled"):
        send_push_later(ids, rows[0])
    return created


LEVEL_ICONS = {"info": "info", "success": "circle-check", "warning": "triangle-exclamation-point", "danger": "circle-exclamation-point", "accent": "sparkles", "neutral": "bell"}


def client(note):
    data = note.as_json()
    data["icon"] = data["icon"] if icons.exists(data["icon"]) else LEVEL_ICONS.get(data["level"], "bell")
    data["svg"] = icons.symbol(data["icon"])
    return data


def unseen(user, since):
    queryset = Notification.objects.filter(recipient=user)
    unread = queryset.filter(read_at__isnull=True).count()
    items = []
    newest = since
    if since is not None:
        found = list(queryset.filter(id__gt=since).select_related("actor").order_by("id")[:20])
        items = [client(n) for n in found]
        if found:
            newest = found[-1].pk
    else:
        newest = queryset.order_by("-id").values_list("id", flat=True).first() or 0
    return {"items": items, "unread": unread, "since": newest}


def latest(user, limit=30, only_unread=False):
    queryset = Notification.objects.filter(recipient=user).select_related("actor")
    if only_unread:
        queryset = queryset.filter(read_at__isnull=True)
    return [client(n) for n in queryset[:limit]]


def mark_read(user, ids=None):
    queryset = Notification.objects.filter(recipient=user, read_at__isnull=True)
    if ids is not None:
        queryset = queryset.filter(pk__in=ids)
    count = queryset.update(read_at=timezone.now())
    live.poke_users([user.pk])
    return count


def cleanup():
    days = settings().get("keep_days")
    if not days:
        return 0
    cutoff = timezone.now() - datetime.timedelta(days=int(days))
    return Notification.objects.filter(created_at__lt=cutoff).delete()[0]


def push_payload(note):
    push = conf.get("PUSH")
    return {
        "title": note.title,
        "body": note.body,
        "url": note.link or "",
        "level": note.level,
        "icon": conf.asset(push.get("icon")) if push.get("icon") else "",
        "badge": conf.asset(push.get("badge")) if push.get("badge") else "",
        "tag": note.key or f"cc-{note.level}",
    }


def send_push(user_ids, note):
    push = conf.get("PUSH")
    levels = push.get("levels")
    if levels and note.level not in levels:
        return 0
    try:
        from pywebpush import WebPushException, webpush
    except ImportError:
        log.warning("PUSH is enabled but pywebpush is not installed. Run pip install django-cc-admin[push].")
        return 0
    payload = json.dumps(push_payload(note))
    sent = 0
    for sub in PushSubscription.objects.filter(user_id__in=user_ids):
        try:
            webpush(
                subscription_info=sub.as_info(),
                data=payload,
                vapid_private_key=push.get("vapid_private_key"),
                vapid_claims=dict(push.get("vapid_claims") or {}),
                ttl=int(push.get("ttl") or 3600),
            )
            sent += 1
            PushSubscription.objects.filter(pk=sub.pk).update(last_used_at=timezone.now())
        except WebPushException as error:
            status = getattr(getattr(error, "response", None), "status_code", None)
            if status in (404, 410):
                sub.delete()
            else:
                log.warning("Push to %s failed: %s", sub.pk, error)
        except Exception as error:
            log.warning("Push to %s failed: %s", sub.pk, error)
    return sent


def send_push_later(user_ids, note):
    thread = threading.Thread(target=send_push, args=(list(user_ids), note), daemon=True)
    thread.start()
    return thread


EVENTS = {"created", "updated", "deleted"}


def _format(template, obj, actor, event, model):
    if callable(template):
        return template(obj, event)
    if not template:
        return ""
    try:
        return str(template).format(obj=obj, actor=actor or "", event=event, model=model)
    except (AttributeError, KeyError, IndexError, ValueError):
        return str(template)


def _link(rule, obj, event):
    value = rule.get("link", "change")
    opts = obj._meta
    if callable(value):
        return value(obj)
    try:
        if value == "change" and event != "deleted":
            return reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[obj.pk])
        if value in ("change", "list"):
            return reverse(f"admin:{opts.app_label}_{opts.model_name}_changelist")
    except NoReverseMatch:
        return ""
    return conf.link(value) if value else ""


def run_rule(rule, obj, event):
    actor = current.user()
    when = rule.get("when")
    if when is not None:
        check = conf.as_callable(when)
        if not check(obj, event):
            return []
    model = str(obj._meta.verbose_name)
    title = _format(rule.get("title") or "{model} {event}", obj, actor, event, model)
    body = _format(rule.get("body", ""), obj, actor, event, model)
    to = rule.get("to", "staff")
    if isinstance(to, str) and conf.DOTTED.match(to):
        to = conf.as_callable(to)
    return notify(
        to(obj) if callable(to) else to,
        title,
        body=body,
        link=_link(rule, obj, event),
        level=rule.get("level", "info"),
        icon=rule.get("icon", ""),
        sound=rule.get("sound", ""),
        actor=actor,
        key=rule.get("key", f"{obj._meta.label_lower}:{event}"),
        push=rule.get("push", True),
        exclude_actor=rule.get("exclude_actor", True),
    )


def _rules_for(sender):
    label = f"{sender._meta.app_label}.{sender._meta.model_name}"
    for rule in settings().get("rules") or []:
        if str(rule.get("model", "")).lower() == label:
            yield rule


def _events(rule):
    value = rule.get("on", "created")
    return {value} if isinstance(value, str) else set(value)


def on_save(sender, instance, created, raw=False, **kwargs):
    if raw or not enabled():
        return
    event = "created" if created else "updated"
    for rule in _rules_for(sender):
        if event in _events(rule):
            try:
                run_rule(rule, instance, event)
            except Exception:
                log.exception("Notification rule failed for %s", sender)


def on_delete(sender, instance, **kwargs):
    if not enabled():
        return
    for rule in _rules_for(sender):
        if "deleted" in _events(rule):
            try:
                run_rule(rule, instance, "deleted")
            except Exception:
                log.exception("Notification rule failed for %s", sender)


def connect():
    post_save.connect(on_save, dispatch_uid="cc_admin_notify_save")
    post_delete.connect(on_delete, dispatch_uid="cc_admin_notify_delete")
