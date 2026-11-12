###############
# Qiyas Sadıqov CC
###############

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

LEVELS = [
    ("info", _("Info")),
    ("success", _("Success")),
    ("warning", _("Warning")),
    ("danger", _("Danger")),
    ("accent", _("Accent")),
    ("neutral", _("Neutral")),
]


class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cc_notifications", verbose_name=_("recipient"))
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+", verbose_name=_("actor"))
    title = models.CharField(_("title"), max_length=200)
    body = models.TextField(_("body"), blank=True)
    link = models.CharField(_("link"), max_length=500, blank=True)
    level = models.CharField(_("level"), max_length=16, choices=LEVELS, default="info")
    icon = models.CharField(_("icon"), max_length=64, blank=True)
    sound = models.CharField(_("sound"), max_length=32, blank=True)
    key = models.CharField(_("key"), max_length=120, blank=True)
    data = models.JSONField(_("data"), default=dict, blank=True)
    created_at = models.DateTimeField(_("created at"), default=timezone.now, db_index=True)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
        indexes = [models.Index(fields=["recipient", "read_at"], name="cc_notif_unread")]

    def __str__(self):
        return self.title

    @property
    def is_read(self):
        return self.read_at is not None

    def as_json(self):
        return {
            "id": self.pk,
            "title": self.title,
            "body": self.body,
            "link": self.link,
            "level": self.level,
            "icon": self.icon,
            "sound": self.sound,
            "key": self.key,
            "data": self.data,
            "at": self.created_at.isoformat(),
            "read": self.read_at is not None,
            "actor": (self.actor.get_full_name() or self.actor.get_username()) if self.actor_id and self.actor else "",
        }


class PushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cc_push_subscriptions", verbose_name=_("user"))
    endpoint = models.TextField(_("endpoint"))
    endpoint_hash = models.CharField(max_length=64, unique=True, editable=False)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=100)
    user_agent = models.CharField(_("browser"), max_length=300, blank=True)
    created_at = models.DateTimeField(_("created at"), default=timezone.now)
    last_used_at = models.DateTimeField(_("last used"), null=True, blank=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("push subscription")
        verbose_name_plural = _("push subscriptions")

    def __str__(self):
        return self.user_agent[:60] or self.endpoint[:60]

    def as_info(self):
        return {"endpoint": self.endpoint, "keys": {"p256dh": self.p256dh, "auth": self.auth}}
