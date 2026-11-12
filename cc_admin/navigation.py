###############
# Qiyas Sadıqov CC
###############

from django.contrib import admin
from django.utils.text import capfirst

from . import conf

GUESSES = [
    (("user", "member", "account", "profile", "staff", "person", "people"), "users"),
    (("group", "role", "permission"), "shield"),
    (("customer", "client", "contact", "lead"), "circle-user"),
    (("order", "invoice", "receipt", "purchase"), "receipt"),
    (("product", "item", "sku", "inventory", "stock"), "package"),
    (("category", "folder", "collection"), "folder"),
    (("tag", "label", "keyword"), "tag"),
    (("payment", "transaction", "charge", "refund"), "credit-card"),
    (("ship", "delivery", "shipment", "courier"), "truck"),
    (("post", "article", "page", "blog", "story", "news"), "newspaper"),
    (("comment", "message", "chat", "review", "feedback"), "message-square"),
    (("image", "photo", "media", "file", "upload", "asset", "document"), "image"),
    (("setting", "config", "option", "preference"), "settings"),
    (("log", "event", "audit", "history", "activity"), "activity"),
    (("task", "job", "schedule", "cron", "queue"), "list-checks"),
    (("site", "domain", "redirect", "url", "link"), "globe"),
    (("email", "mail", "newsletter", "subscriber"), "mail"),
    (("notification", "alert"), "bell"),
    (("project", "workspace", "team"), "briefcase"),
    (("token", "key", "secret", "session", "auth"), "key-round"),
    (("country", "city", "location", "address", "region"), "map-pin"),
    (("coupon", "discount", "promo", "voucher"), "ticket-percent"),
    (("report", "metric", "stat", "analytic"), "chart-line"),
    (("plan", "subscription", "price", "billing"), "wallet"),
    (("course", "lesson", "student", "teacher", "class"), "graduation-cap"),
    (("event", "booking", "reservation", "appointment"), "calendar"),
]


def guess_icon(*names):
    joined = " ".join(n.lower() for n in names if n)
    for words, icon in GUESSES:
        if any(w in joined for w in words):
            return icon
    return "box"


def model_icon(app_label, model_name):
    icons = conf.get("SIDEBAR").get("icons") or {}
    return (
        icons.get(f"{app_label}.{model_name}")
        or icons.get(app_label + "." + model_name.lower())
        or guess_icon(model_name)
    )


def app_icon(app_label):
    icons = conf.get("SIDEBAR").get("icons") or {}
    return icons.get(app_label) or {"auth": "shield", "sites": "globe", "admin": "activity"}.get(app_label, "layers")


def available_apps(request, context=None):
    if context is not None:
        apps = context.get("available_apps")
        if apps is not None:
            return apps
    site = getattr(request, "_cc_admin_site", None) or admin.site
    try:
        return site.get_app_list(request)
    except Exception:
        return []


def _allowed(item, request):
    permission = item.get("permission")
    if permission is None:
        return True
    return conf.rule(permission, request)


def _badge(item, request):
    badge = item.get("badge")
    if badge is None:
        return None
    value = conf.call(badge, request) if callable(badge) or "." in str(badge) else badge
    if value in (None, "", 0):
        return None
    return value


def _mark_active(groups, path):
    best = None
    for group in groups:
        for item in group["items"]:
            url = item.get("url") or ""
            if not url or url.startswith(("http", "#")):
                continue
            if path == url or (url != "/" and path.startswith(url) and url.count("/") > 2):
                if best is None or len(url) > len(best.get("url", "")):
                    best = item
    if best:
        best["active"] = True
        for group in groups:
            if best in group["items"]:
                group["active"] = True


def build(request, context=None):
    sidebar = conf.get("SIDEBAR")
    groups = []
    for spec in sidebar.get("navigation") or []:
        spec = conf.evaluate(spec, request)
        if not spec or not _allowed(spec, request):
            continue
        items = []
        for raw in spec.get("items", []):
            if not _allowed(raw, request):
                continue
            items.append(
                {
                    "title": raw.get("title", ""),
                    "icon": raw.get("icon") or "dot",
                    "url": conf.link(raw.get("link"), request),
                    "badge": _badge(raw, request),
                    "badge_variant": raw.get("badge_variant", "accent"),
                    "external": str(raw.get("link", "")).startswith("http"),
                    "active": bool(conf.evaluate(raw.get("active"), request)) if raw.get("active") is not None else False,
                }
            )
        if items:
            groups.append(
                {
                    "title": spec.get("title", ""),
                    "icon": spec.get("icon") or "layers",
                    "collapsible": spec.get("collapsible", False),
                    "items": items,
                    "key": spec.get("key") or (spec.get("title") or "nav").lower().replace(" ", "-"),
                }
            )
    if sidebar.get("show_all_applications"):
        seen = {item["url"] for group in groups for item in group["items"]}
        for app in available_apps(request, context):
            items = []
            for model in app.get("models", []):
                url = model.get("admin_url") or model.get("add_url")
                if not url or url in seen:
                    continue
                items.append(
                    {
                        "title": capfirst(model.get("name", "")),
                        "icon": model_icon(app["app_label"], model.get("object_name", "")),
                        "url": url,
                        "add_url": model.get("add_url"),
                        "model": f"{app['app_label']}.{model.get('object_name', '').lower()}",
                        "badge": None,
                    }
                )
            if items:
                groups.append(
                    {
                        "title": app.get("name", ""),
                        "icon": app_icon(app["app_label"]),
                        "collapsible": True,
                        "items": items,
                        "key": app["app_label"],
                    }
                )
    _mark_active(groups, request.path)
    return groups


def model_entries(request, context=None):
    entries = []
    for app in available_apps(request, context):
        for model in app.get("models", []):
            entries.append(
                {
                    "title": capfirst(model.get("name", "")),
                    "app": app.get("name", ""),
                    "icon": model_icon(app["app_label"], model.get("object_name", "")),
                    "url": model.get("admin_url") or "",
                    "add_url": model.get("add_url") or "",
                    "key": f"{app['app_label']}.{model.get('object_name', '').lower()}",
                }
            )
    return entries


def tabs(request, opts=None):
    found = []
    for spec in conf.get("TABS") or []:
        models = [m.lower() for m in spec.get("models", [])]
        pages = spec.get("pages", [])
        hit = False
        if opts is not None and f"{opts.app_label}.{opts.model_name}" in models:
            hit = True
        if any(request.path.startswith(conf.link(p, request)) for p in pages):
            hit = True
        if not hit:
            continue
        for raw in spec.get("items", []):
            if not _allowed(raw, request):
                continue
            url = conf.link(raw.get("link"), request)
            found.append(
                {
                    "title": raw.get("title", ""),
                    "icon": raw.get("icon"),
                    "url": url,
                    "badge": _badge(raw, request),
                    "active": bool(conf.evaluate(raw.get("active"), request))
                    if raw.get("active") is not None
                    else request.get_full_path() == url or request.path == url,
                }
            )
        if found and not any(t["active"] for t in found):
            for t in found:
                if t["url"].split("?")[0] == request.path and "?" not in t["url"]:
                    t["active"] = True
        break
    return found
