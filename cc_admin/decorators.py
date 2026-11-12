###############
# Qiyas Sadıqov CC
###############

import functools

from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.text import slugify

from .icons import icon

TONES = ("neutral", "accent", "success", "warning", "danger", "info")


def _initials(text):
    words = [w for w in str(text).replace("@", " ").replace(".", " ").split() if w]
    return "".join(w[0] for w in words[:2]).upper() or "?"


def render_label(value, label):
    if isinstance(value, (list, tuple)) and len(value) == 2:
        key, text = value
    else:
        key, text = value, value
    if key in (None, ""):
        return format_html('<span class="cc-muted">—</span>')
    tone = "neutral"
    if isinstance(label, dict):
        tone = label.get(key) or label.get(str(key)) or label.get(text) or "neutral"
    elif isinstance(label, str) and label in TONES:
        tone = label
    return format_html('<span class="cc-badge cc-tone-{}">{}</span>', tone, text)


def render_header(value):
    if not isinstance(value, (list, tuple)):
        value = (value,)
    title = value[0] if value else ""
    subtitle = value[1] if len(value) > 1 else ""
    avatar = value[2] if len(value) > 2 else _initials(title)
    if isinstance(avatar, dict):
        image = avatar.get("image")
        avatar_html = (
            format_html('<img src="{}" alt="">', image) if image else format_html("{}", avatar.get("text", _initials(title)))
        )
    elif isinstance(avatar, str) and avatar.startswith(("http://", "https://", "/")):
        avatar_html = format_html('<img src="{}" alt="">', avatar)
    elif avatar is False:
        avatar_html = None
    else:
        avatar_html = format_html("{}", avatar)
    return format_html(
        '<span class="cc-cell-head">{}<span><b>{}</b>{}</span></span>',
        format_html('<span class="cc-avatar" data-seed="{}">{}</span>', title, avatar_html) if avatar_html else "",
        title,
        format_html("<small>{}</small>", subtitle) if subtitle else "",
    )


def render_image(value):
    url = getattr(value, "url", value) if value else ""
    if not url:
        return format_html('<span class="cc-muted">—</span>')
    return format_html('<img class="cc-thumb" src="{}" alt="" loading="lazy">', url)


def render_progress(value):
    if isinstance(value, (list, tuple)) and len(value) == 2:
        done, total = value
    else:
        done, total = value, 100
    try:
        share = max(0.0, min(100.0, float(done or 0) / float(total or 1) * 100))
    except (TypeError, ValueError):
        share = 0.0
    tone = "success" if share >= 100 else "danger" if share < 15 else "accent"
    return format_html(
        '<span class="cc-progress-cell cc-tone-{}"><span class="cc-progress-bar"><i style="width:{}%"></i></span><em>{}%</em></span>',
        tone,
        f"{share:.1f}",
        f"{share:.0f}",
    )


def display(
    function=None,
    *,
    boolean=None,
    ordering=None,
    description=None,
    empty_value=None,
    label=None,
    header=False,
    copy=False,
    mono=False,
    tags=False,
    image=False,
    progress=False,
):
    def decorator(func):
        if label is None and not header and not copy and not mono and not tags and not image and not progress:
            wrapped = func
        else:

            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                value = func(*args, **kwargs)
                if header:
                    return render_header(value)
                if image:
                    return render_image(value)
                if progress:
                    return render_progress(value)
                if label is not None:
                    return render_label(value, label)
                if tags:
                    return format_html(
                        '<span class="cc-tags">{}</span>',
                        format_html_join("", '<span class="cc-badge cc-tone-neutral">{}</span>', ((v,) for v in value or [])),
                    )
                if value in (None, ""):
                    return value
                if copy:
                    return format_html(
                        '<span class="cc-copy{}"><span>{}</span><button type="button" data-copy="{}" title="Copy">{}</button></span>',
                        " cc-mono" if mono else "",
                        value,
                        value,
                        icon("copy"),
                    )
                return format_html('<span class="cc-mono">{}</span>', value)

        decorated = admin.display(
            wrapped,
            boolean=boolean,
            ordering=ordering,
            description=description,
            empty_value=empty_value,
        )
        decorated.cc_label = label
        decorated.cc_header = header
        return decorated

    if function is None:
        return decorator
    return decorator(function)


def action(
    function=None,
    *,
    description=None,
    permissions=None,
    icon=None,
    variant="default",
    url_path=None,
    confirm=None,
    attrs=None,
    new_tab=False,
):
    def decorator(func):
        decorated = admin.action(func, permissions=permissions, description=description)
        decorated.cc_icon = icon
        decorated.cc_variant = variant
        decorated.cc_url_path = url_path or slugify(func.__name__.replace("_", "-"))
        decorated.cc_confirm = confirm
        decorated.cc_attrs = attrs or {}
        decorated.cc_new_tab = new_tab
        return decorated

    if function is None:
        return decorator
    return decorator(function)
