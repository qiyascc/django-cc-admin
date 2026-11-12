###############
# Qiyas Sadıqov CC
###############

import contextvars
import re
from functools import lru_cache
from pathlib import Path

from django.utils.html import escape
from django.utils.safestring import mark_safe

SPRITE = Path(__file__).parent / "data" / "icons.svg"
SYMBOL = re.compile(r'<symbol id="([^"]+)" viewBox="([^"]+)">(.*?)</symbol>', re.S)

BASE = {
    "arrow-down",
    "arrow-left",
    "arrow-right",
    "arrow-up",
    "arrow-up-right",
    "book-open",
    "box",
    "calendar",
    "check",
    "chevron-down",
    "chevron-left",
    "chevron-right",
    "chevrons-up-down",
    "circle-check",
    "circle-exclamation-point",
    "clock",
    "columns-3",
    "command",
    "copy",
    "corner-down-left",
    "download",
    "ellipsis",
    "external-link",
    "eye",
    "file-text",
    "funnel",
    "grip-vertical",
    "house",
    "info",
    "keyboard",
    "layers",
    "layout-dashboard",
    "list-filter",
    "lock",
    "log-out",
    "menu",
    "monitor",
    "moon",
    "palette",
    "panel-left",
    "pencil",
    "pin",
    "pin-off",
    "plus",
    "rotate-ccw-clock",
    "rows-3",
    "search",
    "settings",
    "sliders-horizontal",
    "sparkles",
    "star",
    "sun",
    "trash",
    "triangle-exclamation-point",
    "user",
    "x",
    "dot",
    "bell",
    "refresh-cw",
    "check-check",
}

_used = contextvars.ContextVar("cc_admin_icons", default=None)


@lru_cache(maxsize=1)
def symbols():
    text = SPRITE.read_text(encoding="utf-8")
    return {name: (box, body.strip()) for name, box, body in SYMBOL.findall(text)}


def exists(name):
    return name in symbols()


def reset():
    _used.set(set())


def collected():
    used = _used.get()
    return set(used) if used else set()


def use(name):
    name = str(name or "dot")
    if name not in symbols():
        name = "dot"
    used = _used.get()
    if used is None:
        used = set()
        _used.set(used)
    used.add(name)
    return name


def icon(name, cls="", label=None):
    name = use(name)
    extra = f" {escape(cls)}" if cls else ""
    aria = f' role="img" aria-label="{escape(label)}"' if label else ' aria-hidden="true"'
    return mark_safe(f'<svg class="cc-icon{extra}"{aria}><use href="#cc-i-{name}"></use></svg>')


def sprite(extra=()):
    names = BASE | collected() | {n for n in extra if n}
    table = symbols()
    parts = []
    for name in sorted(names):
        if name in table:
            box, body = table[name]
            parts.append(f'<symbol id="cc-i-{name}" viewBox="{box}">{body}</symbol>')
    return mark_safe(
        '<svg xmlns="http://www.w3.org/2000/svg" class="cc-sprite" aria-hidden="true" '
        'style="position:absolute;width:0;height:0;overflow:hidden">' + "".join(parts) + "</svg>"
    )


def symbol(name):
    found = symbols().get(str(name or ""))
    if not found:
        return ""
    box, body = found
    return f'<symbol id="cc-i-{name}" viewBox="{box}">{body}</symbol>'
