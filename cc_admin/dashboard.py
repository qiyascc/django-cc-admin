###############
# Qiyas Sadıqov CC
###############

import datetime
import re

from django.apps import apps as django_apps
from django.contrib.admin.models import LogEntry
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.text import capfirst

from . import charts, conf, navigation

DOTTED = re.compile(r"^[A-Za-z_]\w*(\.[A-Za-z_]\w*)+$")

WIDTHS = {
    "kpi": 3,
    "chart": 8,
    "table": 6,
    "list": 4,
    "progress": 4,
    "models": 12,
    "activity": 4,
    "links": 4,
    "recent": 4,
    "heatmap": 12,
    "html": 12,
    "note": 12,
    "apps": 12,
}


def source(value, request, *args):
    if callable(value):
        return conf.evaluate(value, request, *args)
    if isinstance(value, str) and DOTTED.match(value):
        try:
            func = conf.as_callable(value)
        except ImportError:
            return value
        return conf.evaluate(func, request, *args)
    return value


def default_widgets():
    return [
        {"type": "models", "title": "Your data"},
        {"type": "activity", "title": "Recent activity", "width": 6},
        {"type": "recent", "title": "Recently opened", "width": 6},
    ]


def _kpi(spec, request):
    value = source(spec.get("value"), request)
    data = value if isinstance(value, dict) else {"value": value}
    for key in ("delta", "delta_label", "spark", "footer", "prefix", "suffix", "tone"):
        if key not in data and key in spec:
            data[key] = source(spec[key], request)
    raw = data.get("value")
    if isinstance(raw, (int, float)) or hasattr(raw, "as_tuple"):
        data["display"] = charts.compact(raw, data.get("prefix", ""), data.get("suffix", ""), spec.get("decimals"))
        data["full"] = charts.compact(raw, data.get("prefix", ""), data.get("suffix", ""), 2) if raw >= 1000 else ""
    else:
        data["display"] = raw if raw is not None else "—"
    delta = data.get("delta")
    if isinstance(delta, (int, float)):
        data["delta_tone"] = "up" if delta > 0 else "down" if delta < 0 else "flat"
        if spec.get("inverse"):
            data["delta_tone"] = {"up": "down-good", "down": "up-bad"}.get(data["delta_tone"], "flat")
        data["delta_text"] = f"{'+' if delta > 0 else ''}{delta:.1f}%".replace(".0%", "%")
    elif delta:
        data["delta_tone"] = "flat"
        data["delta_text"] = str(delta)
    if data.get("spark"):
        data["spark_svg"] = charts.spark(data["spark"], height=spec.get("spark_height", 44))
    return data


def _chart(spec, request):
    data = source(spec.get("data"), request) or {}
    kind = spec.get("kind", "area")
    prefix, suffix = spec.get("prefix", ""), spec.get("suffix", "")
    height = spec.get("height", 240)
    if kind == "donut":
        items = data.get("items", data) if isinstance(data, dict) else data
        return {"svg": charts.donut(items, prefix=prefix, suffix=suffix, center_label=spec.get("center_label", "total"))}
    labels, series = data.get("labels", []), data.get("series", [])
    if kind in ("bar", "stacked-bar"):
        svg = charts.bar(labels, series, height=height, stacked=kind == "stacked-bar", prefix=prefix, suffix=suffix)
    else:
        svg = charts.line(
            labels,
            series,
            height=height,
            area=kind in ("area", "stacked-area"),
            stacked=kind == "stacked-area",
            smooth=spec.get("smooth", True),
            prefix=prefix,
            suffix=suffix,
        )
    return {"svg": svg, "summary": source(spec.get("summary"), request)}


def _cell(cell):
    if isinstance(cell, dict):
        return cell
    return {"text": cell}


def _table(spec, request):
    data = source(spec.get("data"), request) or {}
    headers = data.get("headers", spec.get("headers", []))
    rows = [[_cell(c) for c in row] for row in data.get("rows", [])]
    return {"headers": headers, "rows": rows, "align": data.get("align", spec.get("align", []))}


def _items(spec, request):
    items = source(spec.get("items"), request) or []
    out = []
    for item in items:
        item = dict(item)
        if "link" in item:
            item["url"] = conf.link(item["link"], request)
        if spec["type"] == "progress":
            total = float(item.get("total", 100) or 1)
            item["share"] = max(0.0, min(100.0, float(item.get("value", 0)) / total * 100))
        out.append(item)
    return {"items": out}


def _model_counts(spec, request):
    wanted = [m.lower() for m in spec.get("models") or []]
    rows = []
    for entry in navigation.model_entries(request):
        if wanted and entry["key"] not in wanted:
            continue
        try:
            model = django_apps.get_model(entry["key"])
            count = model._default_manager.count()
        except Exception:
            count = None
        rows.append({**entry, "count": count, "count_text": charts.compact(count) if count is not None else "—"})
    if wanted:
        rows.sort(key=lambda r: wanted.index(r["key"]))
    return {"items": rows[: spec.get("limit", 12)]}


def _activity(spec, request):
    entries = LogEntry.objects.select_related("content_type", "user").order_by("-action_time")
    if spec.get("scope", "all") == "mine":
        entries = entries.filter(user=request.user)
    rows = []
    for entry in entries[: spec.get("limit", 8)]:
        url = None
        if entry.content_type_id and not entry.is_deletion():
            try:
                url = reverse(
                    f"admin:{entry.content_type.app_label}_{entry.content_type.model}_change",
                    args=[entry.object_id],
                )
            except NoReverseMatch:
                url = None
        rows.append(
            {
                "entry": entry,
                "url": url,
                "verb": "added" if entry.is_addition() else "deleted" if entry.is_deletion() else "changed",
                "model": capfirst(entry.content_type.model_class()._meta.verbose_name) if entry.content_type and entry.content_type.model_class() else "",
                "who": entry.user.get_short_name() or entry.user.get_username() if entry.user_id else "",
            }
        )
    return {"items": rows}


def _heatmap(spec, request):
    data = source(spec.get("data"), request) or {}
    weeks = int(spec.get("weeks", 26))
    today = timezone.localdate()
    start = today - datetime.timedelta(days=today.weekday() + (weeks - 1) * 7)
    counts = {}
    for key, value in (data.items() if isinstance(data, dict) else data):
        if isinstance(key, datetime.datetime):
            key = key.date()
        if isinstance(key, str):
            key = datetime.date.fromisoformat(key[:10])
        counts[key] = counts.get(key, 0) + (value or 0)
    peak = max(counts.values(), default=0) or 1
    columns, months, last_month = [], [], None
    total = 0
    for w in range(weeks):
        cells = []
        for d in range(7):
            day = start + datetime.timedelta(days=w * 7 + d)
            value = counts.get(day, 0)
            if day <= today:
                total += value
            level = 0 if not value else min(4, 1 + int(value / peak * 3.999))
            cells.append({"date": day, "value": value, "level": level, "future": day > today})
        first = start + datetime.timedelta(days=w * 7)
        if first.month != last_month:
            if not months or w - months[-1][0] >= 3:
                months.append((w, first.strftime("%b")))
            last_month = first.month
        columns.append(cells)
    return {"weeks": columns, "months": months, "total": total, "count": weeks}


def _note(spec, request):
    return {"text": source(spec.get("text"), request), "tone": spec.get("tone", "info")}


def _html(spec, request, context):
    extra = source(spec.get("context"), request) or {}
    if spec.get("template"):
        return {"html": render_to_string(spec["template"], {**context.flatten(), **extra}, request=request)}
    return {"html": source(spec.get("html"), request)}


BUILDERS = {
    "kpi": _kpi,
    "chart": _chart,
    "table": _table,
    "list": _items,
    "progress": _items,
    "links": _items,
    "models": _model_counts,
    "activity": _activity,
    "heatmap": _heatmap,
    "note": _note,
}


def build(request, context):
    settings = conf.get("DASHBOARD")
    specs = settings.get("widgets")
    specs = default_widgets() if specs is None else source(specs, request)
    widgets = []
    for spec in specs or []:
        spec = dict(source(spec, request) or {})
        if not spec:
            continue
        if spec.get("permission") is not None and not conf.call(spec["permission"], request):
            continue
        kind = spec.get("type", "html")
        if kind in ("html", "template"):
            data = _html(spec, request, context)
            kind = "html"
        elif kind in ("recent", "apps"):
            data = {}
        else:
            data = BUILDERS.get(kind, lambda s, r: {})(spec, request)
        widgets.append(
            {
                "type": kind,
                "spec": spec,
                "data": data,
                "width": max(1, min(12, int(spec.get("width", WIDTHS.get(kind, 4))))),
                "url": conf.link(spec.get("link"), request) if spec.get("link") else "",
                "template": f"cc_admin/widgets/{kind}.html",
            }
        )
    return widgets
