# Dashboard

The admin index page becomes a dashboard: a greeting with the date, an optional title and subtitle, and a twelve column grid of widgets. You describe the widgets in settings and point each one at its data. django-cc-admin draws the cards, the numbers and the charts. Charts are plain SVG made on the server, so there is no chart library to load and they pick up the theme colours on their own.

```{image} ../screenshots/dashboard.jpg
:alt: The example shop dashboard with KPIs, an area chart and a donut chart
```

## The default dashboard

With no `DASHBOARD` setting you get three widgets: a card with every model and its row count ("Your data"), the latest changes from the admin log, and the records you opened lately. Once you set `widgets`, you replace that list completely.

## Settings

```python
CC_ADMIN = {
    "DASHBOARD": {
        "greeting": True,
        "title": None,
        "subtitle": "Here is how the store did over the last 30 days.",
        "callback": "shop.dashboard.context",
        "widgets": [
            {"type": "kpi", "title": "Revenue", "icon": "wallet", "value": "shop.dashboard.revenue"},
            {"type": "chart", "kind": "area", "title": "Revenue", "data": "shop.dashboard.revenue_chart", "prefix": "$", "width": 8},
            {"type": "chart", "kind": "donut", "title": "Order status", "data": "shop.dashboard.status_split", "width": 4},
        ],
    },
}
```

`greeting`
: Show the date and "Good morning, Aysel" above the grid. The words change with the time of day on the user's computer. Default `True`.

`title`
: A heading of your own. It replaces the "Good morning" line and keeps the date above it. Can be a callable that takes the request.

`subtitle`
: A line of text under the heading. Can be a callable.

`callback`
: A function, or a dotted path to one, that receives `(request, context)` and returns a dict. The dict is added to the template context of the dashboard. That is useful for `html` widgets that render your own templates.

`widgets`
: The list of widgets. The whole list may also be a callable or a dotted path that returns the list, so you can build a different dashboard per user.

## How widgets get their data

Every data key of a widget (`value`, `data`, `items`, `text` and so on) takes one of three things:

- a plain value: `"value": 42`,
- a function that takes the request: `"value": revenue`,
- a dotted path to such a function, as a string: `"value": "shop.dashboard.revenue"`.

Dotted paths are imported the first time they are used. A string that is not a dotted path is used as it is. The function is called every time the dashboard is drawn, and again when [live updates](live-updates.md) refresh the dashboard.

Here is a complete data module for three widgets:

```python
import datetime
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import Order

PAID = ["paid", "shipped", "delivered"]


def revenue(request):
    since = timezone.now() - datetime.timedelta(days=30)
    total = Order.objects.filter(status__in=PAID, created_at__gte=since).aggregate(s=Sum("total"))["s"] or Decimal("0")
    return {"value": total, "prefix": "$", "delta": 18.6, "delta_label": "vs last 30 days"}


def revenue_chart(request):
    start = timezone.localdate() - datetime.timedelta(days=29)
    rows = (
        Order.objects.filter(status__in=PAID, created_at__date__gte=start)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("total"))
    )
    found = {row["day"]: float(row["total"]) for row in rows}
    days = [start + datetime.timedelta(days=i) for i in range(30)]
    return {
        "labels": [day.strftime("%b %-d") for day in days],
        "series": [{"name": "Revenue", "values": [found.get(day, 0) for day in days]}],
    }


def status_split(request):
    rows = Order.objects.values("status").annotate(n=Count("id")).order_by("-n")
    return [{"label": row["status"].title(), "value": row["n"]} for row in rows]
```

## The grid

The grid has twelve columns. `width` sets how many a widget takes, from 1 to 12. Widgets flow left to right and wrap to the next row. Below 1180 pixels the grid adapts on its own: widgets of 3 to 5 columns take half a row and widgets of 7 to 9 columns take a full row. On phones every widget takes the full width.

When you leave `width` out, each type has its own default:

| Type | Default width |
| --- | --- |
| `kpi` | 3 |
| `chart` | 8 |
| `table` | 6 |
| `contributions` | 8 |
| `tracker` | 6 |
| `list`, `progress`, `links`, `activity`, `recent`, `team` | 4 |
| `models`, `heatmap`, `cohort`, `html`, `note`, `apps` | 12 |

So four `kpi` widgets fill one row, and a `chart` with a `list` next to it fills another.

## Keys every widget takes

| Key | Meaning |
| --- | --- |
| `type` | The widget type. Defaults to `html`. |
| `title` | The card heading. |
| `subtitle` | A smaller line under the heading. |
| `icon` | A Lucide icon next to the heading. |
| `width` | 1 to 12. |
| `link` | Makes the heading clickable. A URL name, a path or a full URL. |
| `link_text` | The text of the link in the card head, for types that show one ("View all" by default). |
| `permission` | Who sees the widget. See [Permissions](permissions.md). A widget the user may not see is left out and the rest of the grid closes up. |

## Widget types

### kpi

A single number with an optional change, a label and a sparkline.

```python
{"type": "kpi", "title": "Revenue", "icon": "wallet", "value": "shop.dashboard.revenue", "link": "admin:shop_order_changelist"}
```

`value` returns a number, or a dict with more detail:

```python
def revenue(request):
    return {
        "value": 73386,
        "prefix": "$",
        "delta": 18.6,
        "delta_label": "vs last 30 days",
        "spark": [1200, 1900, 1600, 2400, 2100, 2800, 3100],
        "footer": "Paid orders only",
    }
```

| Key | Meaning |
| --- | --- |
| `value` | The number. Large numbers are shortened: 73386 becomes `73.4k`, and hovering shows the full value. Strings are shown as they are. |
| `prefix`, `suffix` | Text before and after the number, like `$` or `%`. |
| `delta` | The change in percent. Positive is shown green with an up arrow, negative red with a down arrow. |
| `delta_label` | Text after the change, such as "vs last 30 days". |
| `spark` | A list of numbers drawn as a small line at the bottom of the card. |
| `footer` | A muted line of text. |

These keys can also sit on the widget itself instead of in the returned dict. On the widget you can also set:

| Widget key | Meaning |
| --- | --- |
| `decimals` | Decimal places for numbers under 1000. By default whole numbers show none and others show one. |
| `inverse` | `True` for numbers where going down is good, like refunds or response time. The colours of the change swap. |
| `tone` | Tints the card: `accent`, `success`, `warning`, `danger`, `info` or `neutral`. |
| `spark_height` | Height of the sparkline in pixels. Default 44. |

### chart

```python
{"type": "chart", "kind": "area", "title": "Revenue", "subtitle": "Daily, paid orders only", "data": "shop.dashboard.revenue_chart", "summary": "shop.dashboard.revenue_summary", "prefix": "$", "width": 8, "height": 250}
```

`kind` is one of:

| Kind | Draws |
| --- | --- |
| `line` | Lines. |
| `area` | Lines with a filled area under them. The default. |
| `stacked-area` | Areas stacked on top of each other. |
| `bar` | Bars side by side. |
| `stacked-bar` | Bars stacked. |
| `donut` | A ring with a legend and percentages. |

Line, area and bar charts take labels and one or more series:

```python
{
    "labels": ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"],
    "series": [
        {"name": "Web", "values": [120, 140, 135, 160, 170, 190]},
        {"name": "Mobile app", "values": [80, 95, 110, 120, 150, 165]},
        {"name": "Previous year", "values": [90, 100, 110, 115, 120, 125], "color": "var(--cc-border-strong)"},
    ],
}
```

Series take their colours from the theme in order. Give `color` to pick one yourself, either a CSS colour or one of the theme variables such as `var(--cc-success)`.

A donut takes a list of slices:

```python
[
    {"label": "Delivered", "value": 1830, "color": "var(--cc-success)"},
    {"label": "Shipped", "value": 131, "color": "var(--cc-accent)"},
    {"label": "Refunded", "value": 127},
]
```

Other chart keys:

| Key | Meaning |
| --- | --- |
| `prefix`, `suffix` | Added to axis labels and tooltips. |
| `height` | Height of the plot in pixels. Default 240. |
| `smooth` | Curved lines for `line` and `area`. Default `True`. |
| `center_label` | The word under the total in a donut. Default `"total"`. |
| `summary` | Big numbers above the plot: a list of `{"label", "value", "note"}`, or a function that returns one. |

```python
def revenue_summary(request):
    return [
        {"label": "Gross revenue", "value": "$73,386"},
        {"label": "Paid orders", "value": "304"},
        {"label": "Refunded", "value": "$3,864", "note": "5.3%"},
    ]
```

### table

```python
{"type": "table", "title": "Top products", "data": "shop.dashboard.top_products", "width": 7, "link": "admin:shop_product_changelist"}
```

```python
def top_products(request):
    return {
        "headers": ["Product", "Units", "Revenue", "Stock"],
        "align": ["", "right", "right", "right"],
        "rows": [
            [
                {"text": "Ergonomic Chair", "sub": "Furniture", "link": "/admin/shop/product/12/change/"},
                "412",
                "$53,118",
                {"text": "Low", "badge": "danger"},
            ],
        ],
    }
```

A cell is plain text or a dict with `text`, `sub` (a second line), `link`, `badge` (a tone, which turns the cell into a badge) or `html` (already safe HTML).

### list

```python
{"type": "list", "title": "Latest orders", "items": "shop.dashboard.latest_orders", "width": 5, "link": "admin:shop_order_changelist"}
```

```python
def latest_orders(request):
    return [
        {
            "title": "Leyla Aliyeva",
            "subtitle": "NW-24871 · Web",
            "meta": "$129.00",
            "badge": "Paid",
            "badge_tone": "info",
            "avatar": True,
            "link": "/admin/shop/order/871/change/",
        },
    ]
```

Each item takes `title`, `subtitle`, `meta` (text on the right), `link`, `icon`, `avatar` (`True` for initials from the title), `image` (a picture URL), `badge` and `badge_tone`.

### progress

Horizontal bars, each showing a share of a total.

```python
{"type": "progress", "title": "Revenue by category", "items": "shop.dashboard.category_share", "width": 5}
```

```python
[
    {"label": "Furniture", "value": 31200, "total": 73400, "display": "$31,200", "tone": "accent"},
    {"label": "Lighting", "value": 18100, "total": 73400, "display": "$18,100", "tone": "info"},
]
```

`value` and `total` make the bar (`total` defaults to 100). `display` is the text shown instead of the raw value, `meta` adds a muted note and `tone` colours the bar.

### links

A card of shortcuts.

```python
{"type": "links", "title": "Quick links", "items": [
    {"title": "Add a product", "text": "Opens an empty form", "icon": "plus", "link": "admin:shop_product_add"},
    {"title": "Pending orders", "icon": "clock", "link": "/admin/shop/order/?status__in=pending"},
]}
```

### heatmap

A calendar of coloured squares, one per day, like a GitHub contribution graph.

```python
{"type": "heatmap", "title": "Order activity", "subtitle": "Orders per day, last twelve months", "data": "shop.dashboard.order_days", "unit": "orders", "weeks": 52}
```

`data` returns a dict of dates to counts. Keys may be `date`, `datetime` or ISO strings:

```python
def order_days(request):
    start = timezone.localdate() - datetime.timedelta(days=370)
    rows = Order.objects.filter(created_at__date__gte=start).annotate(d=TruncDate("created_at")).values("d").annotate(n=Count("id"))
    return {row["d"]: row["n"] for row in rows}
```

`weeks` sets the length (default 26) and `unit` the word used in the tooltips.

### models

Every model the user may see with its row count, or only the ones you list:

```python
{"type": "models", "title": "Your data"}
{"type": "models", "title": "Store", "models": ["shop.order", "shop.product", "shop.customer"], "width": 6}
```

`limit` sets the number of models shown (default 12). Each entry links to its list and has a quick "add" button.

### activity

The latest entries of the admin log: who added, changed or deleted what.

```python
{"type": "activity", "title": "Recent changes", "width": 6, "limit": 6}
```

`scope` is `"all"` (default) or `"mine"`, and `limit` sets the number of rows (default 8).

### recent

The records the current user opened lately, newest first. The list is kept in the browser, so it costs the server nothing.

```python
{"type": "recent", "title": "Recently opened", "width": 6}
```

### contributions

The admin log as a calendar for the current user or the whole team. Days link to the [activity page](activity.md).

```python
{"type": "contributions", "title": "Your activity", "icon": "activity", "scope": "me", "weeks": 30, "width": 8}
```

`scope` is `"me"` (default) or `"all"`. `weeks` defaults to 26. The widget follows the `ACTIVITY` settings, so it is hidden if the user may not see that activity.

### team

Who made the most changes over the last `days` days (default 30), with a bar for each person. Only shown to users who may see other people's activity.

```python
{"type": "team", "title": "Team", "icon": "users", "days": 30, "limit": 6, "width": 4}
```

### cohort

A retention table. Each row is a group with a size, and each cell shows what share of that group is still active after a number of periods.

```python
{"type": "cohort", "title": "Customer retention", "subtitle": "Share of new customers who ordered again", "data": "shop.dashboard.retention"}
```

```python
{
    "headers": ["Month 0", "+1", "+2", "+3"],
    "rows": [
        {"label": "Aug 2026", "sub": "48 customers", "total": 48, "values": [48, 19, 14, 11]},
        {"label": "Sep 2026", "sub": "52 customers", "total": 52, "values": [52, 23, 17, None]},
    ],
}
```

`None` leaves a cell empty, for periods that have not happened yet. Set `"percent": False` on the widget to show the raw numbers instead of shares.

### tracker

A row of small coloured bars, like an uptime chart.

```python
{"type": "tracker", "title": "Fulfilment", "subtitle": "Last 60 days", "data": "shop.dashboard.fulfilment"}
```

```python
[
    {
        "label": "Orders shipped on time",
        "summary": "52 of 60 days",
        "items": [
            {"tone": "success", "title": "Mon Nov 9 · 12 orders, 1 open"},
            {"tone": "warning", "title": "Tue Nov 10 · 9 orders, 4 open"},
        ],
    },
]
```

Each item is a dict with `tone` and `title` (shown on hover), or just a tone string.

### note

A coloured box of text, for a message to the team.

```python
{"type": "note", "title": "Heads up", "icon": "info", "text": "Prices change on Monday.", "tone": "warning"}
```

### html

Your own template or HTML inside the grid.

```python
{"type": "html", "title": "Shipping map", "template": "shop/dashboard_map.html", "context": "shop.dashboard.map_context", "width": 6}
{"type": "html", "html": "shop.dashboard.banner_html", "bare": True}
```

With `template`, the template is rendered with the dashboard context plus whatever `context` returns. With `html`, the returned string is inserted as it is, so return a safe string built with `format_html`. `bare: True` drops the card frame around it.

### apps

The classic list of apps and models, as on the stock admin index page.

```python
{"type": "apps", "title": "All models"}
```

## A dashboard per user

Because `widgets` may be a callable, you can build the list from the request:

```python
def widgets(request):
    found = [
        {"type": "kpi", "title": "Orders today", "value": "shop.dashboard.orders_today"},
    ]
    if request.user.has_perm("billing.view_invoice"):
        found.append({"type": "kpi", "title": "Revenue", "value": "shop.dashboard.revenue"})
    found.append({"type": "activity", "title": "Recent changes", "scope": "mine", "width": 12})
    return found


CC_ADMIN = {"DASHBOARD": {"widgets": widgets}}
```

For simple cases, the `permission` key on each widget does the same with less code.

## Keeping it fast

Every data function runs each time the dashboard is drawn. A few habits help:

- Aggregate in the database with `annotate`, `aggregate` and `values`, not in Python loops.
- Cache expensive numbers for a minute or two with Django's cache framework.
- Use `select_related` when a list widget reads related objects.
- Put slow widgets lower on the page or behind a `permission`, so only the people who need them pay for them.

Live updates redraw the dashboard when the data behind it changes, at most once every `dashboard_interval` seconds (30 by default). See [Live updates](live-updates.md).

A finished dashboard with every widget type is in the [live order dashboard](../examples/live-dashboard.md) recipe.
