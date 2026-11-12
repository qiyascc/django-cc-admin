###############
# Qiyas Sadıqov CC
###############

import asyncio
import hashlib
import json
import time

from asgiref.sync import sync_to_async
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.handlers.asgi import ASGIRequest
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django.views.generic import TemplateView

from . import activity, conf, live, navigation, notify
from .admin import plain
from .models import LEVELS, Notification, PushSubscription


def search(request, site):
    settings = conf.get("COMMAND_PALETTE")
    query = request.GET.get("q", "").strip()
    if not settings.get("enabled") or not settings.get("search_models") or len(query) < settings.get("min_length", 2):
        return JsonResponse({"results": []})
    limit = max(1, min(int(settings.get("limit", 5)), 25))
    request._cc_admin_site = site
    results = []
    for model, model_admin in site._registry.items():
        if not model_admin.get_search_fields(request) or not model_admin.has_view_permission(request):
            continue
        opts = model._meta
        try:
            queryset = model_admin.get_queryset(request)
            queryset, _unused = model_admin.get_search_results(request, queryset, query)
            objects = list(queryset[:limit])
        except Exception:
            continue
        for obj in objects:
            try:
                url = reverse(f"{site.name}:{opts.app_label}_{opts.model_name}_change", args=[obj.pk], current_app=site.name)
            except NoReverseMatch:
                continue
            results.append(
                {
                    "title": plain(str(obj))[:120],
                    "model": capfirst(opts.verbose_name),
                    "icon": navigation.model_icon(opts.app_label, opts.object_name),
                    "url": url,
                }
            )
    if settings.get("search_callback"):
        extra = conf.call(settings["search_callback"], request, query) or []
        results = [
            {"title": str(r.get("title", "")), "model": str(r.get("subtitle", r.get("model", ""))), "icon": r.get("icon", "arrow-right"), "url": conf.link(r.get("link") or r.get("url"), request)}
            for r in extra
        ] + results
    return JsonResponse({"results": results[:60]})


def _activity_context(request, site, user=None):
    year = activity.parse_year(request.GET.get("year"))
    day = activity.parse_day(request.GET.get("day"))
    data = activity.overview(request, user, year, day)
    query = f"?year={year}&" if year else "?"
    return {
        **site.each_context(request),
        "activity": data,
        "years": activity.years(user),
        "base_query": query,
        "team_url": activity.url(request) if activity.can_see_others(request) and activity.settings().get("team") else "",
        "is_popup": False,
    }


def activity_index(request, site):
    request._cc_admin_site = site
    if not activity.enabled(request):
        raise PermissionDenied
    if not activity.settings().get("team") or not activity.can_see_others(request):
        return HttpResponseRedirect(activity.url(request, request.user))
    context = _activity_context(request, site)
    data = context["activity"]
    if request.GET.get("partial"):
        return TemplateResponse(request, "cc_admin/activity/feed.html", context)
    context.update(
        {
            "title": _("Activity"),
            "people": activity.people(request, data["start"], data["end"]),
            "subject": None,
        }
    )
    return TemplateResponse(request, "cc_admin/activity/team.html", context)


def activity_user(request, site, user_id):
    request._cc_admin_site = site
    target = get_object_or_404(get_user_model(), pk=user_id)
    if not activity.can_see(request, target):
        raise PermissionDenied
    context = _activity_context(request, site, target)
    if request.GET.get("partial"):
        return TemplateResponse(request, "cc_admin/activity/feed.html", context)
    subject = activity.person(target, request)
    context.update({"title": subject["name"], "subject": subject, "is_self": target.pk == request.user.pk})
    return TemplateResponse(request, "cc_admin/activity/user.html", context)


class AdminPageView(TemplateView):
    model_admin = None
    admin_site = None
    title = ""
    subtitle = ""
    icon = None
    permission_required = ()
    template_name = "cc_admin/page.html"

    def get_site(self):
        if self.model_admin is not None:
            return self.model_admin.admin_site
        if self.admin_site is not None:
            return self.admin_site
        from django.contrib import admin

        return admin.site

    def has_permission(self, request):
        perms = self.permission_required
        if isinstance(perms, str):
            perms = (perms,)
        if callable(perms):
            return bool(perms(request))
        return request.user.has_perms(perms)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        site = self.get_site()
        context = {**site.each_context(self.request), **super().get_context_data(**kwargs)}
        context.setdefault("title", self.title)
        context.setdefault("subtitle", self.subtitle)
        if self.model_admin is not None:
            context.setdefault("opts", self.model_admin.opts)
        context["cc_page"] = self
        return context


def live_poll(request, site):
    request._cc_admin_site = site
    if not live.enabled(request):
        raise PermissionDenied
    return JsonResponse(live.collect(request, request.GET), encoder=DjangoJSONEncoder)


def _frame(data):
    return "data: " + json.dumps(data, cls=DjangoJSONEncoder) + "\n\n"


def _signature(data):
    return json.dumps({k: v for k, v in data.items() if k != "t"}, sort_keys=True, cls=DjangoJSONEncoder)


def live_stream(request, site):
    request._cc_admin_site = site
    if not live.enabled(request):
        raise PermissionDenied
    settings = live.settings()
    seconds = max(5, int(settings.get("stream_seconds") or 25))
    interval = max(1, int(settings.get("interval") or 5))
    state = dict(request.GET.items())

    def advance(data):
        if data.get("since") is not None:
            state["since"] = str(data["since"])
        state["badges"] = "0"

    def sync_events():
        yield "retry: 2000\n\n"
        last = None
        deadline = time.monotonic() + seconds
        tick = live.bus.tick
        while True:
            data = live.collect(request, state)
            advance(data)
            sig = _signature(data)
            yield _frame(data) if sig != last else ": ping\n\n"
            last = sig
            if time.monotonic() >= deadline:
                return
            tick = live.bus.wait(tick, interval)

    async def async_events():
        yield "retry: 2000\n\n"
        last = None
        deadline = time.monotonic() + seconds
        collect = sync_to_async(live.collect)
        while True:
            data = await collect(request, state)
            advance(data)
            sig = _signature(data)
            yield _frame(data) if sig != last else ": ping\n\n"
            last = sig
            if time.monotonic() >= deadline:
                return
            tick = live.bus.tick
            for _step in range(interval * 4):
                await asyncio.sleep(0.25)
                if live.bus.tick != tick:
                    break

    stream = async_events() if isinstance(request, ASGIRequest) else sync_events()
    response = StreamingHttpResponse(stream, content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


def notifications_page(request, site):
    request._cc_admin_site = site
    if not notify.enabled():
        raise PermissionDenied
    only_unread = request.GET.get("filter") == "unread"
    if request.GET.get("format") == "json":
        return JsonResponse(
            {
                "items": notify.latest(request.user, 30, only_unread),
                "unread": Notification.objects.filter(recipient=request.user, read_at__isnull=True).count(),
            },
            encoder=DjangoJSONEncoder,
        )
    queryset = Notification.objects.filter(recipient=request.user).select_related("actor")
    if only_unread:
        queryset = queryset.filter(read_at__isnull=True)
    page = Paginator(queryset, 30).get_page(request.GET.get("page"))
    context = {
        **site.each_context(request),
        "title": _("Notifications"),
        "page": page,
        "only_unread": only_unread,
        "unread": Notification.objects.filter(recipient=request.user, read_at__isnull=True).count(),
        "can_broadcast": conf.rule(notify.settings().get("broadcast"), request),
    }
    return TemplateResponse(request, "cc_admin/notifications/list.html", context)


def notifications_read(request, site):
    if request.method != "POST":
        raise PermissionDenied
    ids = request.POST.getlist("id")
    count = notify.mark_read(request.user, [int(i) for i in ids if str(i).isdigit()] if ids else None)
    unread = Notification.objects.filter(recipient=request.user, read_at__isnull=True).count()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "marked": count, "unread": unread})
    return HttpResponseRedirect(request.POST.get("next") or reverse(f"{site.name}:cc_notifications"))


def _json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except ValueError:
        return {}


def push_subscribe(request, site):
    push = conf.get("PUSH")
    if request.method != "POST" or not push.get("enabled"):
        raise PermissionDenied
    data = _json_body(request)
    endpoint = str(data.get("endpoint") or "")
    keys = data.get("keys") or {}
    if not endpoint.startswith("https://") or not keys.get("p256dh") or not keys.get("auth"):
        return JsonResponse({"ok": False}, status=400)
    digest = hashlib.sha256(endpoint.encode()).hexdigest()
    PushSubscription.objects.update_or_create(
        endpoint_hash=digest,
        defaults={
            "user": request.user,
            "endpoint": endpoint,
            "p256dh": str(keys["p256dh"])[:200],
            "auth": str(keys["auth"])[:100],
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:300],
        },
    )
    return JsonResponse({"ok": True})


def push_unsubscribe(request, site):
    if request.method != "POST":
        raise PermissionDenied
    endpoint = str(_json_body(request).get("endpoint") or "")
    digest = hashlib.sha256(endpoint.encode()).hexdigest()
    PushSubscription.objects.filter(user=request.user, endpoint_hash=digest).delete()
    return JsonResponse({"ok": True})


def push_test(request, site):
    if request.method != "POST":
        raise PermissionDenied
    notify.notify(request.user, _("Test notification"), body=_("If you can read this, notifications work on this device."), level="success", icon="bell-ring", key="cc-test")
    return JsonResponse({"ok": True})


SERVICE_WORKER = """self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (event) { event.waitUntil(self.clients.claim()); });
self.addEventListener("push", function (event) {
  var data = {};
  try { data = event.data ? event.data.json() : {}; } catch (e) { data = { title: event.data ? event.data.text() : "" }; }
  event.waitUntil(self.registration.showNotification(data.title || "Admin", {
    body: data.body || "", icon: data.icon || undefined, badge: data.badge || undefined,
    tag: data.tag || undefined, renotify: !!data.tag, data: { url: data.url || "%(home)s" }
  }));
});
self.addEventListener("notificationclick", function (event) {
  event.notification.close();
  var url = (event.notification.data && event.notification.data.url) || "%(home)s";
  event.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (list) {
    for (var i = 0; i < list.length; i++) { if (list[i].url.indexOf(url) >= 0 && "focus" in list[i]) return list[i].focus(); }
    return self.clients.openWindow(url);
  }));
});
"""


def service_worker(request, site):
    home = reverse(f"{site.name}:index")
    response = HttpResponse(SERVICE_WORKER % {"home": home}, content_type="application/javascript")
    response["Service-Worker-Allowed"] = home
    response["Cache-Control"] = "no-cache"
    return response


class BroadcastForm(forms.Form):
    to = forms.ChoiceField(label=_("Send to"))
    title = forms.CharField(label=_("Title"), max_length=200)
    body = forms.CharField(label=_("Message"), widget=forms.Textarea(attrs={"rows": 3}), required=False)
    link = forms.CharField(label=_("Link"), max_length=500, required=False, help_text=_("A path like /admin/shop/order/ or a full URL."))
    level = forms.ChoiceField(label=_("Style"), choices=LEVELS, initial="info")
    sound = forms.ChoiceField(label=_("Sound"), required=False)
    push = forms.BooleanField(label=_("Also send as a push notification"), required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import Group

        choices = [("staff", _("All staff")), ("superuser", _("Superusers"))]
        choices += [(f"group:{g}", _("Group: %(name)s") % {"name": g}) for g in Group.objects.values_list("name", flat=True)]
        User = get_user_model()
        choices += [(f"user:{u.get_username()}", u.get_full_name() or u.get_username()) for u in User.objects.filter(is_staff=True, is_active=True).order_by(User.USERNAME_FIELD)]
        self.fields["to"].choices = choices
        self.fields["sound"].choices = [("", _("Default for the style"))] + [(s, s.title()) for s in SOUNDS]
        from .widgets import SegmentedWidget, SwitchWidget

        self.fields["level"].widget = SegmentedWidget(choices=LEVELS)
        self.fields["push"].widget = SwitchWidget()


SOUNDS = ["chime", "pop", "ping", "bell", "alert", "sparkle", "blip", "cash", "knock", "none"]


def broadcast(request, site):
    request._cc_admin_site = site
    if not notify.enabled() or not conf.rule(notify.settings().get("broadcast"), request):
        raise PermissionDenied
    form = BroadcastForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        sent = notify.notify(
            data["to"],
            data["title"],
            body=data["body"],
            link=conf.link(data["link"]) if data["link"] else "",
            level=data["level"],
            sound=data["sound"],
            actor=request.user,
            push=data["push"],
        )
        messages.success(request, ngettext("Sent to %(n)s person.", "Sent to %(n)s people.", len(sent)) % {"n": len(sent)})
        return HttpResponseRedirect(reverse(f"{site.name}:cc_notifications_send"))
    context = {**site.each_context(request), "title": _("Send a notification"), "form": form, "sounds": SOUNDS}
    return TemplateResponse(request, "cc_admin/notifications/send.html", context)
