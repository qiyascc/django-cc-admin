###############
# Qiyas Sadıqov CC
###############

import re

from django.utils.translation import gettext_lazy as _

from . import conf

ACTIONS = [
    ("palette", _("Command palette"), "global", "mod+k"),
    ("help", _("Show keyboard shortcuts"), "global", "?"),
    ("search", _("Focus search"), "global", "/"),
    ("dashboard", _("Go to dashboard"), "global", "g d"),
    ("activity", _("Go to activity"), "global", "g a"),
    ("site", _("Go to site"), "global", "g s"),
    ("theme", _("Appearance panel"), "global", "t"),
    ("menu", _("Collapse menu"), "global", "["),
    ("next_row", _("Next row"), "list", "j"),
    ("prev_row", _("Previous row"), "list", "k"),
    ("select_row", _("Select row"), "list", "x"),
    ("select_all", _("Select all rows"), "list", "shift+x"),
    ("open_row", _("Open row"), "list", ["o", "enter"]),
    ("open_row_tab", _("Open row in a new tab"), "list", "shift+o"),
    ("expand_row", _("Expand row"), "list", "space"),
    ("add", _("Add new"), "list", "n"),
    ("filters", _("Open filters"), "list", "f"),
    ("columns", _("Choose columns"), "list", "c"),
    ("export", _("Export current view"), "list", "e"),
    ("prev_page", _("Previous page"), "list", "arrowleft"),
    ("next_page", _("Next page"), "list", "arrowright"),
    ("save", _("Save"), "form", "mod+enter"),
    ("save_continue", _("Save and keep editing"), "form", "mod+s"),
    ("save_add", _("Save and add another"), "form", "mod+shift+enter"),
    ("next_tab", _("Next tab"), "form", "alt+arrowright"),
    ("prev_tab", _("Previous tab"), "form", "alt+arrowleft"),
    ("history", _("Open history"), "form", "g h"),
    ("back", _("Back to the list"), "form", "g l"),
    ("delete", _("Delete this record"), "form", None),
]

SCOPES = {"global": _("Anywhere"), "list": _("Lists"), "form": _("Forms"), "custom": _("Your shortcuts")}

ALIASES = {
    "cmd": "mod",
    "command": "mod",
    "ctrl": "mod",
    "control": "mod",
    "meta": "mod",
    "option": "alt",
    "opt": "alt",
    "esc": "escape",
    "return": "enter",
    "left": "arrowleft",
    "right": "arrowright",
    "up": "arrowup",
    "down": "arrowdown",
    "del": "delete",
    "spacebar": "space",
    " ": "space",
}
MODIFIERS = ("mod", "alt", "shift")
SPACES = re.compile(r"\s+")


def normalize_combo(combo):
    text = str(combo).strip().lower()
    if text == "+":
        text = "plus"
    elif text.endswith("++"):
        text = text[:-2] + "+plus"
    parts = [ALIASES.get(p.strip(), p.strip()) for p in text.split("+")]
    mods = [m for m in MODIFIERS if m in parts[:-1]]
    return "+".join(mods + [parts[-1]])


def normalize(value):
    if value in (None, False, "", []):
        return []
    if isinstance(value, str):
        value = [value]
    found = []
    for item in value:
        steps = [normalize_combo(step) for step in SPACES.split(str(item).strip()) if step]
        if steps:
            found.append(" ".join(steps[:3]))
    return found


def client_config(request):
    settings = conf.get("SHORTCUTS")
    if not settings.get("enabled"):
        return {"enabled": False}
    overrides = settings.get("keys") or {}
    actions = []
    for key, label, scope, default in ACTIONS:
        keys = normalize(overrides[key]) if key in overrides else normalize(default)
        actions.append({"id": key, "label": str(label), "scope": scope, "keys": keys, "default": keys})
    for i, raw in enumerate(settings.get("custom") or []):
        raw = conf.evaluate(raw, request)
        if not raw or (raw.get("permission") is not None and not conf.rule(raw["permission"], request)):
            continue
        keys = normalize(raw.get("keys"))
        if not keys:
            continue
        actions.append(
            {
                "id": raw.get("id") or f"custom_{i}",
                "label": str(raw.get("title", "")),
                "scope": raw.get("scope", "custom"),
                "keys": keys,
                "default": keys,
                "url": conf.link(raw.get("link"), request) if raw.get("link") else "",
                "click": raw.get("click", ""),
                "new_tab": bool(raw.get("new_tab")),
            }
        )
    return {
        "enabled": True,
        "editable": bool(settings.get("user_editable")),
        "scopes": {k: str(v) for k, v in SCOPES.items()},
        "actions": actions,
    }
