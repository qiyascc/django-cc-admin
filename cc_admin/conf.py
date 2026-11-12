###############
# Qiyas Sadıqov CC
###############

import inspect
from functools import lru_cache

from django.conf import settings
from django.core.signals import setting_changed
from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse
from django.utils.module_loading import import_string

DEFAULTS = {
    "SITE_TITLE": None,
    "SITE_HEADER": None,
    "SITE_SUBHEADER": None,
    "SITE_URL": None,
    "SITE_LOGO": None,
    "SITE_ICON": None,
    "SITE_FAVICON": None,
    "THEME": "aurora",
    "THEMES": None,
    "THEME_SWITCHER": True,
    "LAYOUT": None,
    "COLOR_SCHEME": "auto",
    "DENSITY": "comfortable",
    "FONTS": True,
    "TOKENS": {},
    "ENVIRONMENT": None,
    "STYLES": [],
    "SCRIPTS": [],
    "SIDEBAR": {},
    "TABS": [],
    "DASHBOARD": {},
    "COMMAND_PALETTE": {},
    "SHORTCUTS": True,
    "LOGIN": {},
    "USER_LINKS": [],
    "FOOTER": None,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "WARN_UNSAVED_FORMS": True,
    "LIST_EXPORT": True,
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
