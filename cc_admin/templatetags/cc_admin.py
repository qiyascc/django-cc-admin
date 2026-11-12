###############
# Qiyas Sadıqov CC
###############

import json

from django import template
from django.contrib.admin.views.main import PAGE_VAR
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import CheckboxInput, CheckboxSelectMultiple, RadioSelect
from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse
from django.utils.html import escape, format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .. import __version__, activity, charts, conf, dashboard, icons, navigation, shortcuts, themes

register = template.Library()


def _site(context):
    request = context.get("request")
    return getattr(request, "_cc_admin_site", None)


def _environment(request):
    value = conf.get("ENVIRONMENT")
    if value is None:
        return None
    value = dashboard.source(value, request)
    if not value:
        return None
    if isinstance(value, str):
        return {"label": value, "tone": "warning"}
    if isinstance(value, (list, tuple)):
        return {"label": value[0], "tone": value[1] if len(value) > 1 else "warning"}
    return value


def _links(key, request, default_icon="arrow-up-right"):
    links = []
    for raw in conf.evaluate(conf.get(key), request) or []:
        raw = conf.evaluate(raw, request)
        if not raw or (raw.get("permission") is not None and not conf.rule(raw["permission"], request)):
            continue
        links.append(
            {
                "title": raw.get("title", ""),
                "icon": raw.get("icon", default_icon),
                "url": conf.link(raw.get("link"), request),
                "new_tab": bool(raw.get("new_tab")),
            }
        )
    return links


def _user_links(request):
    return _links("USER_LINKS", request)


def _languages(request):
    if not conf.get("SHOW_LANGUAGES"):
        return None
    from django.conf import settings as dj
    from django.utils.translation import get_language_info

    try:
        action = reverse("set_language")
    except NoReverseMatch:
        return None
    items = []
    for code, name in dj.LANGUAGES:
        try:
            info = get_language_info(code)
            label = info.get("name_local") or name
        except KeyError:
            label = name
        items.append({"code": code, "name": str(label)})
    return {"action": action, "items": items, "next": request.get_full_path() if request else "/"}


def _fonts():
    value = conf.get("FONTS")
    if isinstance(value, dict):
        return value.get("bundled", True), [conf.asset(f) for f in value.get("files") or []]
    return bool(value), []


def _appearance():
    data = conf.get("APPEARANCE")
    if not conf.get("THEME_SWITCHER"):
        return None
    return {
        "accent": data.get("accent"),
        "accents": data.get("accents") or [],
        "font": data.get("font"),
        "fonts": [{"key": f, "label": "System" if f == "system" else f, "stack": themes.font_stack(f)} for f in themes.user_fonts()],
        "font_size": data.get("font_size"),
        "sizes": themes.SIZES,
        "radius": data.get("radius"),
    }


@register.simple_tag(takes_context=True)
def cc_setup(context):
    icons.reset()
    request = context.get("request")
    site = _site(context)
    resolved = themes.resolve(request)
    theme = resolved["theme"]
    title = conf.evaluate(conf.get("SITE_TITLE"), request) or context.get("site_title") or getattr(site, "site_title", "") or "Django"
    header = conf.evaluate(conf.get("SITE_HEADER"), request) or context.get("site_header") or getattr(site, "site_header", "") or "Admin"
    site_url = conf.evaluate(conf.get("SITE_URL"), request)
    if site_url is None:
        site_url = context.get("site_url")
    palette = conf.get("COMMAND_PALETTE")
    registry = themes.registry()
    bundled_fonts, font_files = _fonts()
    keys = shortcuts.client_config(request)
    environment = _environment(request)
    prefix = conf.get("ENVIRONMENT_TITLE_PREFIX")
    if prefix is True and environment:
        prefix = f"[{environment['label']}]"
    show_activity = request is not None and getattr(request, "user", None) is not None and request.user.is_authenticated and activity.enabled(request)
    data = {
        "version": __version__,
        "title": title,
        "header": header,
        "subheader": conf.evaluate(conf.get("SITE_SUBHEADER"), request) or "",
        "site_url": site_url,
        "logo": conf.themed_asset(conf.get("SITE_LOGO"), request),
        "icon": conf.themed_asset(conf.get("SITE_ICON"), request),
        "favicon": conf.asset(conf.get("SITE_FAVICON"), request),
        "symbol": conf.evaluate(conf.get("SITE_SYMBOL"), request),
        "dropdown": _links("SITE_DROPDOWN", request),
        "title_prefix": prefix or "",
        "languages": _languages(request),
        "back_button": conf.get("SHOW_BACK_BUTTON"),
        "char_counter": conf.get("FORMS").get("char_counter"),
        "font_files": font_files,
        "appearance": _appearance(),
        "activity_url": activity.url(request, request.user) if show_activity else "",
        "activity_team_url": activity.url(request) if show_activity and activity.settings().get("team") and activity.can_see_others(request) else "",
        "activity_menu": show_activity and activity.settings().get("menu"),
        "theme": theme,
        "scheme": resolved["scheme"],
        "density": resolved["density"],
        "layout": resolved["layout"],
        "fonts": bundled_fonts,
        "switcher": conf.get("THEME_SWITCHER"),
        "themes": list(registry.values()),
        "styles": [conf.asset(s, request) for s in conf.get("STYLES") or []],
        "scripts": [conf.asset(s, request) for s in conf.get("SCRIPTS") or []],
        "environment": environment,
        "palette": palette.get("enabled"),
        "shortcuts": keys["enabled"],
        "sidebar_search": conf.get("SIDEBAR").get("search"),
        "pinned": conf.get("SIDEBAR").get("pinned"),
        "user_links": _user_links(request),
        "footer": conf.evaluate(conf.get("FOOTER"), request),
        "show_history": conf.get("SHOW_HISTORY"),
        "show_view_on_site": conf.get("SHOW_VIEW_ON_SITE"),
    }
    if request is not None and getattr(request, "user", None) is not None and request.user.is_authenticated and context.get("has_permission", True):
        data["nav"] = navigation.build(request, context)
        data["models"] = navigation.model_entries(request, context)
    else:
        data["nav"] = []
        data["models"] = []
    data["client"] = json.dumps(
        {
            "theme": theme.key,
            "scheme": resolved["scheme"],
            "density": resolved["density"],
            "layout": resolved["layout"],
            "forcedLayout": resolved["forced_layout"],
            "switcher": bool(conf.get("THEME_SWITCHER")),
            "palette": bool(palette.get("enabled")),
            "searchModels": bool(palette.get("search_models")),
            "minLength": palette.get("min_length", 2),
            "shortcuts": keys,
            "commands": _commands(request),
            "activity": activity.url(request, request.user) if show_activity else "",
            "appearance": bool(_appearance()),
            "perPage": conf.get("LIST_PER_PAGE_OPTIONS") or [],
            "fonts": {f: themes.font_stack(f) for f in themes.user_fonts()},
            "site": site_url or "",
            "themes": {t.key: {"label": t.label, "layout": t.layout, "schemes": list(t.schemes), "css": t.css_key} for t in registry.values()},
            "models": [{"title": m["title"], "app": m["app"], "icon": m["icon"], "url": m["url"], "add": m["add_url"], "key": m["key"]} for m in data["models"]],
            "search": _search_url(request),
        },
        cls=DjangoJSONEncoder,
    ).replace("</", "<\\/")
    context["cc"] = data
    return ""


def _commands(request):
    found = []
    for raw in conf.get("COMMAND_PALETTE").get("commands") or []:
        raw = conf.evaluate(raw, request)
        if not raw or (raw.get("permission") is not None and not conf.rule(raw["permission"], request)):
            continue
        found.append(
            {
                "title": str(raw.get("title", "")),
                "sub": str(raw.get("subtitle", "")),
                "icon": raw.get("icon", "arrow-right"),
                "url": conf.link(raw.get("link"), request),
                "group": str(raw.get("group", "Commands")),
                "keywords": str(raw.get("keywords", "")),
            }
        )
    return found


def _search_url(request):
    site = getattr(request, "_cc_admin_site", None)
    try:
        return reverse(f"{site.name if site else 'admin'}:cc_search")
    except NoReverseMatch:
        return ""


@register.simple_tag
def icon(name, cls="", label=None):
    return icons.icon(name, cls, label)


@register.simple_tag
def cc_sprite():
    return icons.sprite()


@register.simple_tag(takes_context=True)
def cc_nonce(context):
    nonce = context.get("csp_nonce") or getattr(context.get("request"), "csp_nonce", None)
    if nonce:
        return format_html(' nonce="{}"', nonce)
    return ""


@register.simple_tag(takes_context=True)
def cc_media(context, media):
    if not media:
        return ""
    nonce = context.get("csp_nonce") or getattr(context.get("request"), "csp_nonce", None)
    text = str(media)
    if nonce:
        text = text.replace("<script ", format_html('<script nonce="{}" ', nonce)).replace("<link ", format_html('<link nonce="{}" ', nonce))
    return mark_safe(text)


@register.simple_tag(takes_context=True)
def cc_tokens(context):
    css = themes.token_css()
    mine = themes.user_css(context.get("request"))
    html = f'<style id="cc-tokens">{css}</style>' if css else ""
    return mark_safe(html + f'<style id="cc-user-tokens">{mine}</style>')


@register.simple_tag(takes_context=True)
def cc_dashboard(context):
    request = context.get("request")
    cached = getattr(request, "_cc_dashboard", None)
    if cached is None:
        settings = conf.get("DASHBOARD")
        extra = {}
        if settings.get("callback"):
            extra = conf.call(settings["callback"], request, context.flatten()) or {}
        if extra:
            context.update(extra)
        cached = {
            "extra": extra,
            "widgets": dashboard.build(request, context),
            "greeting": settings.get("greeting"),
            "title": conf.evaluate(settings.get("title"), request),
            "subtitle": conf.evaluate(settings.get("subtitle"), request),
        }
        if request is not None:
            request._cc_dashboard = cached
    elif cached["extra"]:
        context.update(cached["extra"])
    return cached


@register.simple_tag(takes_context=True)
def cc_tabs(context):
    request = context.get("request")
    if request is None:
        return []
    return navigation.tabs(request, context.get("opts"))


@register.simple_tag
def cc_filter_hidden(cl):
    owned = set()
    for spec in cl.filter_specs:
        if getattr(spec, "is_input", False):
            owned.update(spec.expected_parameters())
    pairs = []
    for key, values in cl.filter_params.items():
        if key in owned or key == PAGE_VAR:
            continue
        pairs.extend((key, value) for value in values)
    return format_html_join("", '<input type="hidden" name="{}" value="{}">', pairs)


@register.simple_tag
def cc_active_filters(cl):
    return sum(1 for spec in cl.filter_specs if getattr(spec, "used_parameters", None))


@register.filter
def cc_compact(value, prefix=""):
    return charts.compact(value, prefix)


@register.filter
def cc_initials(value):
    words = [w for w in str(value or "").replace("@", " ").replace(".", " ").replace("_", " ").split() if w]
    return "".join(w[0] for w in words[:2]).upper() or "?"


@register.filter
def cc_widget(field):
    bound = getattr(field, "field", None)
    widget = getattr(getattr(bound, "field", None), "widget", None) or getattr(bound, "widget", None)
    if widget is None:
        return ""
    name = type(widget).__name__.lower()
    kinds = [name]
    if isinstance(widget, CheckboxInput):
        kinds.append("cc-w-checkbox")
    if isinstance(widget, (CheckboxSelectMultiple, RadioSelect)):
        kinds.append("cc-w-choices")
    return " ".join(kinds)


@register.filter
def cc_tab_fieldsets(adminform):
    tabs, rest = [], []
    for fieldset in adminform:
        if "tab" in (fieldset.classes or "").split():
            tabs.append(fieldset)
        else:
            rest.append(fieldset)
    return {"tabs": tabs, "rest": rest}


@register.filter
def cc_has_class(fieldset, name):
    return name in (getattr(fieldset, "classes", "") or "").split()


@register.filter
def cc_json(value):
    return mark_safe(escape(json.dumps(value)))


@register.simple_tag
def cc_static(path):
    return static(path)


@register.simple_tag
def cc_spark(values, height=40):
    return charts.spark(values, height)


@register.filter
def cc_split(value, sep=","):
    return [v for v in str(value or "").split(sep) if v]


@register.filter
def cc_get(mapping, key):
    try:
        return mapping.get(key)
    except AttributeError:
        return None


@register.filter
def cc_range(value):
    return range(int(value or 0))


@register.filter
def cc_add(value, other):
    return int(value or 0) + int(other or 0)


@register.filter
def cc_get_index(sequence, index):
    try:
        return sequence[int(index)]
    except (IndexError, TypeError, ValueError, KeyError):
        return None


@register.filter
def cc_qs_join(query, param):
    query = str(query or "?")
    if not query.startswith("?"):
        query = "?" + query
    return query + ("" if query in ("?", "") else "&") + param


def _filter_value(spec, changelist):
    if hasattr(spec, "lookup_gte"):
        low, high = spec.value_from(), spec.value_to()
        if low and high:
            return f"{low} – {high}"
        return f"≥ {low}" if low else f"≤ {high}"
    if hasattr(spec, "selected") and callable(spec.selected):
        labels = [str(c["display"]) for c in spec.choices(changelist) if c.get("selected")]
        return ", ".join(labels)
    if getattr(spec, "is_input", False):
        return spec.value()
    for choice in spec.choices(changelist):
        if choice.get("selected"):
            return str(choice.get("display", ""))
    return ""


@register.simple_tag
def cc_filter_chips(cl):
    chips = []
    for spec in cl.filter_specs:
        if not getattr(spec, "used_parameters", None):
            continue
        value = _filter_value(spec, cl)
        if not value:
            continue
        chips.append(
            {
                "title": spec.title,
                "value": value,
                "url": cl.get_query_string(remove=spec.expected_parameters()),
            }
        )
    return chips


@register.simple_tag
def cc_page_info(cl):
    page = cl.page_num
    paginator = cl.paginator
    info = {"prev": "", "next": "", "start": 0, "end": 0}
    if cl.show_all or not cl.result_count:
        return info
    info["start"] = (page - 1) * cl.list_per_page + 1
    info["end"] = min(page * cl.list_per_page, cl.result_count)
    if page > 1:
        info["prev"] = cl.get_query_string({PAGE_VAR: page - 1})
    if page < paginator.num_pages:
        info["next"] = cl.get_query_string({PAGE_VAR: page + 1})
    return info


@register.simple_tag
def cc_inline_tabs(inline_admin_formsets):
    return [f for f in inline_admin_formsets or [] if getattr(f.opts, "tab", False)]


@register.filter
def cc_has_aside(adminform):
    return any("sidebar" in (fieldset.classes or "").split() for fieldset in adminform)


@register.filter
def cc_collapsible(item):
    if getattr(item, "is_collapsible", False):
        return True
    if getattr(getattr(item, "opts", None), "collapsible", False):
        return True
    return "collapse" in (getattr(item, "classes", "") or "").split()


@register.filter
def cc_collapsed(item):
    return "collapse" in (getattr(item, "classes", "") or "").split()


@register.simple_tag(takes_context=True)
def cc_login(context):
    request = context.get("request")
    login = conf.get("LOGIN")
    return {
        "image": conf.asset(login.get("image"), request),
        "title": conf.evaluate(login.get("title"), request),
        "text": conf.evaluate(login.get("text"), request),
    }


VERB_LABELS = {"added": _("added"), "changed": _("changed"), "deleted": _("deleted")}


@register.filter
def cc_verb(value):
    return VERB_LABELS.get(value, value)


@register.filter
def cc_active_count(people):
    return sum(1 for p in people or [] if p.get("count"))


@register.simple_tag(takes_context=True)
def cc_row_meta(context, cl, index, sortable=False):
    request = getattr(context, "request", None) or context.get("request")
    try:
        obj = cl.result_list[int(index)]
    except (IndexError, TypeError, ValueError):
        return {}
    model_admin = cl.model_admin
    meta = model_admin.cc_row_meta(request, obj) if hasattr(model_admin, "cc_row_meta") else {"pk": obj.pk, "sections": []}
    meta["extra"] = 1 + (1 if sortable else 0)
    return meta


@register.simple_tag(takes_context=True)
def cc_list_flags(context, cl):
    request = getattr(context, "request", None) or context.get("request")
    model_admin = cl.model_admin
    sortable = hasattr(model_admin, "cc_sortable") and request is not None and model_admin.cc_sortable(request)
    return {"sortable": sortable, "sections": bool(getattr(model_admin, "list_sections", None))}


@register.simple_tag
def cc_per_page(cl):
    from ..admin import per_page_options

    model_admin = cl.model_admin
    options = per_page_options(model_admin) if hasattr(model_admin, "cc_row_meta") else []
    return {"options": options, "key": f"{cl.opts.app_label}.{cl.opts.model_name}"}
