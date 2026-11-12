###############
# Qiyas Sadıqov CC
###############

import itertools
import json
import math
from decimal import Decimal

from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

WIDTH = 1000
HEIGHT = 300
IDS = itertools.count(1)


def _num(value):
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def nice_max(value, ticks=4):
    if value <= 0:
        return 1.0, ticks
    raw = value / ticks
    power = 10 ** math.floor(math.log10(raw))
    for step in (1, 2, 2.5, 5, 10):
        if raw <= step * power:
            return step * power * ticks, ticks
    return 10 * power * ticks, ticks


def compact(value, prefix="", suffix="", decimals=None):
    value = _num(value)
    sign = "-" if value < 0 else ""
    value = abs(value)
    for limit, unit in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if value >= limit:
            scaled = value / limit
            text = f"{scaled:.1f}".rstrip("0").rstrip(".") if scaled < 100 else f"{scaled:.0f}"
            return f"{sign}{prefix}{text}{unit}{suffix}"
    if decimals is None:
        decimals = 0 if value == int(value) else 1
    text = f"{value:,.{decimals}f}"
    return f"{sign}{prefix}{text}{suffix}"


def _series(series):
    out = []
    for i, s in enumerate(series):
        if isinstance(s, dict):
            values = [_num(v) for v in s.get("values", [])]
            out.append({"name": s.get("name", ""), "values": values, "color": s.get("color") or f"var(--cc-chart-{i % 6 + 1})"})
        else:
            out.append({"name": "", "values": [_num(v) for v in s], "color": f"var(--cc-chart-{i % 6 + 1})"})
    return out


def _path(points, smooth):
    if not points:
        return ""
    if len(points) == 1:
        x, y = points[0]
        return f"M{x - 1:.1f},{y:.1f}L{x + 1:.1f},{y:.1f}"
    d = [f"M{points[0][0]:.1f},{points[0][1]:.1f}"]
    if not smooth:
        d += [f"L{x:.1f},{y:.1f}" for x, y in points[1:]]
        return "".join(d)
    for i in range(1, len(points)):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        xm = (x0 + x1) / 2
        d.append(f"C{xm:.1f},{y0:.1f} {xm:.1f},{y1:.1f} {x1:.1f},{y1:.1f}")
    return "".join(d)


def _payload(labels, series, prefix, suffix):
    return json.dumps(
        {
            "labels": [str(label) for label in labels],
            "series": [{"name": s["name"], "values": s["values"], "color": s["color"]} for s in series],
            "prefix": prefix,
            "suffix": suffix,
        }
    )


def _x_labels(labels, every=None):
    count = len(labels)
    if count == 0:
        return ""
    every = every or max(1, math.ceil(count / 8))
    spans = []
    for i, label in enumerate(labels):
        if i % every and i != count - 1:
            continue
        if i != count - 1 and count - 1 - i < every / 2 and i % every == 0 and i != 0:
            continue
        left = 0 if count == 1 else i / (count - 1) * 100
        spans.append(f'<span style="left:{left:.3f}%">{escape(label)}</span>')
    return "".join(spans)


def _y_labels(top, ticks, prefix, suffix):
    spans = []
    for t in range(ticks + 1):
        value = top / ticks * t
        spans.append(f'<span style="bottom:{t / ticks * 100:.3f}%">{escape(compact(value, prefix, suffix))}</span>')
    return "".join(spans)


def _grid(ticks):
    lines = []
    for t in range(ticks + 1):
        y = HEIGHT - HEIGHT / ticks * t
        lines.append(f'<line x1="0" x2="{WIDTH}" y1="{y:.1f}" y2="{y:.1f}" class="cc-grid{" cc-grid-base" if t == 0 else ""}"/>')
    return "".join(lines)


def _legend(series):
    if len(series) < 2 and not (series and series[0]["name"]):
        return ""
    items = "".join(
        format_html('<span><i style="background:{}"></i>{}</span>', mark_safe(s["color"]), s["name"]) for s in series
    )
    return f'<div class="cc-chart-legend">{items}</div>'


def line(labels, series, height=240, area=True, smooth=True, stacked=False, prefix="", suffix="", legend=True):
    labels = list(labels)
    series = _series(series)
    count = max([len(labels)] + [len(s["values"]) for s in series]) or 1
    if stacked:
        running = [0.0] * count
        stacked_values = []
        for s in series:
            values = []
            for i in range(count):
                running[i] += s["values"][i] if i < len(s["values"]) else 0
                values.append(running[i])
            stacked_values.append(values)
    else:
        stacked_values = [s["values"] for s in series]
    peak = max([v for values in stacked_values for v in values] + [0])
    top, ticks = nice_max(peak)
    shapes = []
    for index, (s, values) in enumerate(zip(series, stacked_values)):
        points = []
        for i, v in enumerate(values):
            x = WIDTH / 2 if count == 1 else i / (count - 1) * WIDTH
            y = HEIGHT - (v / top * HEIGHT if top else 0)
            points.append((x, y))
        path = _path(points, smooth)
        if area and points:
            if stacked and index:
                prev = stacked_values[index - 1]
                back = [
                    (WIDTH / 2 if count == 1 else i / (count - 1) * WIDTH, HEIGHT - prev[i] / top * HEIGHT)
                    for i in range(len(prev))
                ][::-1]
                fill = path + "L" + _path(back, smooth)[1:] + "Z"
            else:
                fill = path + f"L{points[-1][0]:.1f},{HEIGHT}L{points[0][0]:.1f},{HEIGHT}Z"
            gid = f"ccg{next(IDS)}"
            shapes.append(
                f'<defs><linearGradient id="{gid}" x1="0" x2="0" y1="0" y2="1">'
                f'<stop offset="0" style="stop-color:{s["color"]};stop-opacity:var(--cc-chart-fill-top,.28)"/>'
                f'<stop offset="1" style="stop-color:{s["color"]};stop-opacity:0"/></linearGradient></defs>'
                f'<path d="{fill}" fill="url(#{gid})" class="cc-area"/>'
            )
        shapes.append(f'<path d="{path}" fill="none" style="stroke:{s["color"]}" class="cc-line"/>')
    svg = (
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="none" aria-hidden="true">'
        f"{_grid(ticks)}{''.join(shapes)}</svg>"
    )
    return mark_safe(
        f'<div class="cc-chart cc-chart-line" style="--cc-chart-h:{int(height)}px" data-chart="{escape(_payload(labels, series, prefix, suffix))}" data-top="{top}" data-stacked="{int(stacked)}">'
        f'<div class="cc-chart-body"><div class="cc-chart-y">{_y_labels(top, ticks, prefix, suffix)}</div>'
        f'<div class="cc-chart-plot">{svg}<div class="cc-chart-cursor"></div></div></div>'
        f'<div class="cc-chart-x">{_x_labels(labels)}</div>'
        f"{_legend(series) if legend else ''}</div>"
    )


def bar(labels, series, height=240, stacked=False, prefix="", suffix="", legend=True):
    labels = list(labels)
    series = _series(series)
    count = max([len(labels)] + [len(s["values"]) for s in series]) or 1
    if stacked:
        peak = max([sum(s["values"][i] if i < len(s["values"]) else 0 for s in series) for i in range(count)] + [0])
    else:
        peak = max([v for s in series for v in s["values"]] + [0])
    top, ticks = nice_max(peak)
    columns = []
    for i in range(count):
        bars = []
        for s in series:
            v = s["values"][i] if i < len(s["values"]) else 0
            bars.append(f'<i style="--v:{v / top * 100 if top else 0:.3f}%;background:{s["color"]}"></i>')
        columns.append(f'<div class="cc-bar{" cc-bar-stack" if stacked else ""}" data-i="{i}">{"".join(bars)}</div>')
    labels_html = "".join(f"<span>{escape(label)}</span>" for label in labels)
    return mark_safe(
        f'<div class="cc-chart cc-chart-bar" style="--cc-chart-h:{int(height)}px;--n:{count}" data-chart="{escape(_payload(labels, series, prefix, suffix))}">'
        f'<div class="cc-chart-body"><div class="cc-chart-y">{_y_labels(top, ticks, prefix, suffix)}</div>'
        f'<div class="cc-chart-plot"><svg viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="none" aria-hidden="true">{_grid(ticks)}</svg>'
        f'<div class="cc-bars">{"".join(columns)}</div></div></div>'
        f'<div class="cc-chart-xb">{labels_html}</div>'
        f"{_legend(series) if legend else ''}</div>"
    )


def donut(items, size=168, thickness=22, prefix="", suffix="", center=None, center_label=""):
    rows = []
    for item in items:
        if isinstance(item, dict):
            rows.append((str(item.get("label", "")), _num(item.get("value")), item.get("color")))
        else:
            rows.append((str(item[0]), _num(item[1]), item[2] if len(item) > 2 else None))
    items = rows
    total = sum(v for _, v, _ in items) or 1
    radius = 50 - thickness / 2 / size * 100
    circumference = 2 * math.pi * radius
    offset = 0.0
    rings = []
    legend = []
    for i, (label, value, color) in enumerate(items):
        color = color or f"var(--cc-chart-{i % 6 + 1})"
        length = value / total * circumference
        gap = 0.6 if len(items) > 1 and length > 1.2 else 0
        rings.append(
            f'<circle r="{radius:.3f}" cx="50" cy="50" fill="none" style="stroke:{color}" stroke-width="{thickness / size * 100:.3f}" '
            f'stroke-dasharray="{max(length - gap, 0):.3f} {circumference:.3f}" stroke-dashoffset="{-offset:.3f}" '
            f'data-label="{escape(label)}" data-value="{escape(compact(value, prefix, suffix))}"/>'
        )
        offset += length
        share = value / total * 100
        legend.append(
            f'<li><i style="background:{color}"></i><span>{escape(label)}</span>'
            f"<b>{escape(compact(value, prefix, suffix))}</b><em>{share:.0f}%</em></li>"
        )
    middle = compact(total if center is None else center, prefix, suffix)
    return mark_safe(
        f'<div class="cc-donut"><div class="cc-donut-ring" style="--size:{int(size)}px">'
        f'<svg viewBox="0 0 100 100" aria-hidden="true"><circle r="{radius:.3f}" cx="50" cy="50" fill="none" class="cc-donut-track" stroke-width="{thickness / size * 100:.3f}"/>'
        f'<g transform="rotate(-90 50 50)">{"".join(rings)}</g></svg>'
        f'<div class="cc-donut-center"><b>{escape(middle)}</b><span>{escape(center_label)}</span></div></div>'
        f'<ul class="cc-donut-legend">{"".join(legend)}</ul></div>'
    )


def spark(values, height=40, area=True, color=None):
    values = [_num(v) for v in values]
    if not values:
        return ""
    low, high = min(values), max(values)
    span = (high - low) or 1
    count = len(values)
    points = [
        (WIDTH / 2 if count == 1 else i / (count - 1) * WIDTH, HEIGHT - 12 - (v - low) / span * (HEIGHT - 24))
        for i, v in enumerate(values)
    ]
    color = color or "var(--cc-accent)"
    path = _path(points, True)
    fill = ""
    if area:
        gid = f"ccs{next(IDS)}"
        fill = (
            f'<defs><linearGradient id="{gid}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" style="stop-color:{color};stop-opacity:.25"/>'
            f'<stop offset="1" style="stop-color:{color};stop-opacity:0"/></linearGradient></defs>'
            f'<path d="{path}L{WIDTH},{HEIGHT}L0,{HEIGHT}Z" fill="url(#{gid})"/>'
        )
    return mark_safe(
        f'<svg class="cc-spark" style="height:{int(height)}px" viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="none" aria-hidden="true">'
        f'{fill}<path d="{path}" fill="none" style="stroke:{color}" class="cc-line"/></svg>'
    )


def progress(value, total=100, variant="accent"):
    value, total = _num(value), _num(total) or 1
    share = max(0.0, min(100.0, value / total * 100))
    return format_html('<div class="cc-progress cc-tone-{}"><i style="width:{}%"></i></div>', variant, f"{share:.2f}")
