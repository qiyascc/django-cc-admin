###############
# Qiyas Sadıqov CC
###############

import inspect
import re
from functools import lru_cache

from django.conf import settings
from django.core.signals import setting_changed
from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse
from django.utils.module_loading import import_string

DOTTED = re.compile(r"^[A-Za-z_]\w*(\.[A-Za-z_]\w*){2,}$")

DEFAULTS = {
    "SITE_TITLE": None,
    "SITE_HEADER": None,
    "SITE_SUBHEADER": None,
    "SITE_URL": None,
    "SITE_LOGO": None,
    "SITE_ICON": None,
    "SITE_FAVICON": None,
    "SITE_SYMBOL": None,
    "SITE_DROPDOWN": [],
    "THEME": "aurora",
    "THEMES": None,
    "THEME_ORDER": None,
    "THEME_SWITCHER": True,
    "LAYOUT": None,
    "COLOR_SCHEME": "auto",
    "DENSITY": "comfortable",
    "FONTS": True,
    "COLORS": {},
    "RADIUS": None,
    "TOKENS": {},
    "APPEARANCE": {},
    "ENVIRONMENT": None,
    "ENVIRONMENT_TITLE_PREFIX": False,
    "STYLES": [],
    "SCRIPTS": [],
    "SIDEBAR": {},
    "TABS": [],
    "DASHBOARD": {},
    "COMMAND_PALETTE": {},
    "SHORTCUTS": {},
    "ACTIVITY": {},
    "LIVE": {},
    "NOTIFICATIONS": {},
    "PUSH": {},
    "ANNOUNCEMENTS": [],
    "LOGIN": {},
    "USER_LINKS": [],
    "FOOTER": None,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "SHOW_LANGUAGES": False,
    "WARN_UNSAVED_FORMS": True,
    "LIST_EXPORT": True,
    "LIST_PER_PAGE_OPTIONS": [25, 50, 100, 200],
    "FORMS": {},
}

SIDEBAR_DEFAULTS = {
    "search": True,
    "show_all_applications": True,
    "pinned": True,
    "navigation": [],
}

PALETTE_DEFAULTS = {
    "enabled": True,
    "search_models": True,
    "limit": 5,
    "min_length": 2,
    "commands": [],
    "search_callback": None,
}

SHORTCUT_DEFAULTS = {
    "enabled": True,
    "user_editable": True,
    "keys": {},
    "custom": [],
}

ACTIVITY_DEFAULTS = {
    "enabled": True,
    "view": "staff",
    "others": "superuser",
    "team": True,
    "details": True,
    "weeks": 53,
    "exclude": [],
    "menu": True,
}

LIVE_DEFAULTS = {
    "enabled": True,
    "transport": "poll",
    "url": "/ws/cc-admin/",
    "interval": 5,
    "hidden_interval": 30,
    "stream_seconds": 25,
    "lists": "auto",
    "forms": True,
    "presence": True,
    "dashboard": True,
    "dashboard_interval": 30,
    "badges": True,
    "highlight": True,
}

NOTIFICATION_DEFAULTS = {
    "enabled": True,
    "bell": True,
    "popup": True,
    "position": "bottom-right",
    "duration": 7,
    "max": 4,
    "sound": "chime",
    "sounds": {"success": "chime", "info": "pop", "warning": "bell", "danger": "alert", "accent": "sparkle", "neutral": "blip"},
    "volume": 0.6,
    "desktop": True,
    "desktop_when": "hidden",
    "user_settings": True,
    "broadcast": "superuser",
    "keep_days": 60,
    "admin": True,
    "rules": [],
}

PUSH_DEFAULTS = {
    "enabled": False,
    "vapid_public_key": "",
    "vapid_private_key": "",
    "vapid_claims": {},
    "icon": None,
    "badge": None,
    "ttl": 3600,
    "levels": None,
}

APPEARANCE_DEFAULTS = {
    "accent": True,
    "font": True,
    "font_size": True,
    "radius": True,
    "accents": ["#5b5bd6", "#2563eb", "#0e8a8a", "#16a34a", "#d97706", "#e5484d", "#db2777", "#7c3aed", "#18181b"],
    "fonts": None,
}

FORMS_DEFAULTS = {
    "switches": False,
    "json_editor": True,
    "show_cancel": True,
    "char_counter": True,
}

DASHBOARD_DEFAULTS = {
    "callback": None,
    "greeting": True,
    "title": None,
    "subtitle": None,
    "widgets": None,
}

LOGIN_DEFAULTS = {
    "image": None,
    "title": None,
    "text": None,
    "redirect_after": None,
}


@lru_cache(maxsize=1)
def config():
    data = {**DEFAULTS, **getattr(settings, "CC_ADMIN", {})}
    data["SIDEBAR"] = {**SIDEBAR_DEFAULTS, **(data["SIDEBAR"] or {})}
    data["COMMAND_PALETTE"] = {**PALETTE_DEFAULTS, **(data["COMMAND_PALETTE"] or {})}
    data["DASHBOARD"] = {**DASHBOARD_DEFAULTS, **(data["DASHBOARD"] or {})}
    data["LOGIN"] = {**LOGIN_DEFAULTS, **(data["LOGIN"] or {})}
    shortcuts = data["SHORTCUTS"]
    if isinstance(shortcuts, bool) or shortcuts is None:
        shortcuts = {"enabled": bool(shortcuts)}
    data["SHORTCUTS"] = {**SHORTCUT_DEFAULTS, **shortcuts}
    activity = data["ACTIVITY"]
    if isinstance(activity, bool) or activity is None:
        activity = {"enabled": bool(activity)}
    data["ACTIVITY"] = {**ACTIVITY_DEFAULTS, **activity}
    appearance = data["APPEARANCE"]
    if isinstance(appearance, bool) or appearance is None:
        appearance = {key: bool(appearance) for key in ("accent", "font", "font_size", "radius")}
    data["APPEARANCE"] = {**APPEARANCE_DEFAULTS, **appearance}
    data["FORMS"] = {**FORMS_DEFAULTS, **(data["FORMS"] or {})}
    for key, defaults in (("LIVE", LIVE_DEFAULTS), ("NOTIFICATIONS", NOTIFICATION_DEFAULTS), ("PUSH", PUSH_DEFAULTS)):
        value = data[key]
        if isinstance(value, bool) or value is None:
            value = {"enabled": bool(value)}
        data[key] = {**defaults, **value}
    data["NOTIFICATIONS"]["sounds"] = {**NOTIFICATION_DEFAULTS["sounds"], **(data["NOTIFICATIONS"].get("sounds") or {})}
    return data


def _reset(*, setting, **kwargs):
    if setting == "CC_ADMIN":
        config.cache_clear()


setting_changed.connect(_reset)


def get(key, default=None):
    return config().get(key, default)


def as_callable(value):
    if isinstance(value, str):
        return import_string(value)
    return value


def evaluate(value, request=None, *args):
    if not callable(value):
        return value
    params = [request, *args]
    try:
        signature = inspect.signature(value).parameters.values()
    except (TypeError, ValueError):
        return value(*params)
    if any(p.kind is p.VAR_POSITIONAL for p in signature):
        return value(*params)
    positional = [p for p in signature if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    return value(*params[: len(positional)])


def call(value, request=None, *args):
    if value is None:
        return None
    return evaluate(as_callable(value), request, *args)


def link(value, request=None):
    value = evaluate(value, request)
    if not value:
        return ""
    value = str(value)
    if value.startswith(("/", "http://", "https://", "#", "?", "mailto:")):
        return value
    try:
        return reverse(value)
    except NoReverseMatch:
        return value


def asset(value, request=None):
    value = evaluate(value, request)
    if not value:
        return ""
    value = str(value)
    if value.startswith(("/", "http://", "https://", "data:")):
        return value
    return static(value)


def themed_asset(value, request=None):
    value = evaluate(value, request)
    if not value:
        return None
    if isinstance(value, dict):
        light = asset(value.get("light") or value.get("dark"), request)
        dark = asset(value.get("dark") or value.get("light"), request)
        return {"light": light, "dark": dark}
    url = asset(value, request)
    return {"light": url, "dark": url}


def rule(value, request, *args):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated or not user.is_active:
        return False
    if value is True or value in ("all", "staff", "everyone"):
        return bool(user.is_staff)
    if value in (None, False, "none", "self", "nobody"):
        return False
    if value == "superuser":
        return bool(user.is_superuser)
    if isinstance(value, (list, tuple, set)):
        return any(rule(v, request, *args) for v in value)
    if isinstance(value, str) and value.startswith("group:"):
        return user.groups.filter(name=value[6:]).exists()
    if isinstance(value, str) and value.startswith("perm:"):
        return user.has_perm(value[5:])
    return bool(call(value, request, *args))
