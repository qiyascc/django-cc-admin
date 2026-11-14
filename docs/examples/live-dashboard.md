# Recipe: a live order dashboard

This recipe builds the dashboard of the example shop: four KPIs with sparklines and changes against the previous month, a revenue chart with the previous period behind it, a donut of order statuses, top products, the latest orders, revenue by channel and category, a year of order activity, a retention table and a fulfilment tracker. Then it makes the dashboard update itself while orders come in.

```{image} ../screenshots/dashboard.jpg
:alt: The finished dashboard
```

The models are the ones from the example project: `Order` (with `status`, `channel`, `total`, `created_at` and a `customer`), `OrderItem`, `Product` and `Customer`.

## 1. A module for the numbers

Keep every data function in one module, `shop/dashboard.py`. They all take the request, so they can also be used for per user numbers later.

Start with a few helpers:

```python
import datetime
from decimal import Decimal

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.urls import reverse
from django.utils import timezone

from .models import Customer, Order, OrderItem, Product

PAID = ["paid", "shipped", "delivered"]


def _window(days, offset=0):
    end = timezone.now() - datetime.timedelta(days=offset)
    return end - datetime.timedelta(days=days), end


def _revenue(start, end):
    return Order.objects.filter(status__in=PAID, created_at__gte=start, created_at__lt=end).aggregate(s=Sum("total"))["s"] or Decimal("0")


def _change(now, before):
    if not before:
        return None
    return float((Decimal(now) - Decimal(before)) / Decimal(before) * 100)


def _daily(days, field="total"):
    start = timezone.localdate() - datetime.timedelta(days=days - 1)
    rows = (
        Order.objects.filter(status__in=PAID, created_at__date__gte=start)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(v=Sum(field) if field == "total" else Count("id"))
    )
    found = {r["day"]: float(r["v"] or 0) for r in rows}
    return [found.get(start + datetime.timedelta(days=i), 0) for i in range(days)]
```

## 2. KPIs with a change and a sparkline

```python
def revenue(request):
    now, before = _revenue(*_window(30)), _revenue(*_window(30, 30))
    return {"value": now, "prefix": "$", "delta": _change(now, before), "delta_label": "vs last 30 days", "spark": _daily(30)}


def orders(request):
    start, end = _window(30)
    p_start, p_end = _window(30, 30)
    now = Order.objects.filter(created_at__gte=start, created_at__lt=end).count()
    before = Order.objects.filter(created_at__gte=p_start, created_at__lt=p_end).count()
    return {"value": now, "delta": _change(now, before), "delta_label": "vs last 30 days", "spark": _daily(30, "count")}
```

`_change` returns `None` when there is nothing to compare with, and the card then shows no change.

```python
"widgets": [
    {"type": "kpi", "title": "Revenue", "icon": "wallet", "value": "shop.dashboard.revenue", "link": "admin:shop_order_changelist"},
    {"type": "kpi", "title": "Orders", "icon": "receipt", "value": "shop.dashboard.orders"},
    {"type": "kpi", "title": "Average order", "icon": "chart-line", "value": "shop.dashboard.average_order", "decimals": 0},
    {"type": "kpi", "title": "New customers", "icon": "user-plus", "value": "shop.dashboard.new_customers"},
]
```

## 3. A chart with the previous period behind it

The second series is drawn in a muted colour so the current period stands out:

```python
def revenue_chart(request):
    days = 30
    today = timezone.localdate()
    labels = [(today - datetime.timedelta(days=days - 1 - i)).strftime("%b %-d") for i in range(days)]
    current = _daily(days)
    start = today - datetime.timedelta(days=days * 2 - 1)
    rows = (
        Order.objects.filter(status__in=PAID, created_at__date__gte=start, created_at__date__lt=today - datetime.timedelta(days=days - 1))
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(v=Sum("total"))
    )
    found = {r["day"]: float(r["v"] or 0) for r in rows}
    previous = [found.get(start + datetime.timedelta(days=i), 0) for i in range(days)]
    return {
        "labels": labels,
        "series": [
            {"name": "This period", "values": current},
            {"name": "Previous period", "values": previous, "color": "var(--cc-chart-muted, var(--cc-border-strong))"},
        ],
    }


def revenue_summary(request):
    start, end = _window(30)
    qs = Order.objects.filter(created_at__gte=start, created_at__lt=end)
    paid = qs.filter(status__in=PAID)
    refunds = qs.filter(status="refunded").aggregate(s=Sum("total"))["s"] or 0
    return [
        {"label": "Gross revenue", "value": f"${paid.aggregate(s=Sum('total'))['s'] or 0:,.0f}"},
        {"label": "Paid orders", "value": f"{paid.count():,}"},
        {"label": "Refunded", "value": f"${refunds:,.0f}"},
    ]
```

```python
{"type": "chart", "kind": "area", "title": "Revenue", "subtitle": "Daily, paid orders only", "data": "shop.dashboard.revenue_chart", "summary": "shop.dashboard.revenue_summary", "prefix": "$", "width": 8, "height": 250},
```

## 4. A donut with colours that mean something

Pick colours from the theme's status palette, so "Cancelled" is red in every theme:

```python
def status_split(request):
    rows = Order.objects.values("status").annotate(n=Count("id")).order_by("-n")
    names = dict(Order.Status.choices)
    colors = {
        "delivered": "var(--cc-success)",
        "shipped": "var(--cc-accent)",
        "paid": "var(--cc-info)",
        "pending": "var(--cc-warning)",
        "refunded": "var(--cc-text-3)",
        "cancelled": "var(--cc-danger)",
    }
    return [{"label": names[r["status"]], "value": r["n"], "color": colors.get(r["status"])} for r in rows]
```

```python
{"type": "chart", "kind": "donut", "title": "Order status", "subtitle": "All time", "data": "shop.dashboard.status_split", "width": 4, "center_label": "orders"},
```

## 5. A table and a list that link into the admin

```python
def top_products(request):
    rows = (
        OrderItem.objects.filter(order__status__in=PAID)
        .values("product__id", "product__name", "product__category__name", "product__stock")
        .annotate(units=Sum("quantity"), revenue=Sum(F("quantity") * F("unit_price")))
        .order_by("-revenue")[:6]
    )
    out = []
    for r in rows:
        stock = r["product__stock"]
        out.append([
            {"text": r["product__name"], "sub": r["product__category__name"], "link": reverse("admin:shop_product_change", args=[r["product__id"]])},
            {"text": f"{r['units']:,}"},
            {"text": f"${r['revenue']:,.0f}"},
            {"text": "Low" if stock < 15 else "OK", "badge": "danger" if stock < 15 else "success"},
        ])
    return {"headers": ["Product", "Units", "Revenue", "Stock"], "rows": out, "align": ["", "right", "right", "right"]}


def latest_orders(request):
    tones = {"pending": "warning", "paid": "info", "shipped": "accent", "delivered": "success", "refunded": "neutral", "cancelled": "danger"}
    items = []
    for o in Order.objects.select_related("customer")[:6]:
        items.append({
            "title": o.customer.name,
            "subtitle": f"{o.number} · {o.get_channel_display()}",
            "meta": f"${o.total:,.2f}",
            "badge": o.get_status_display(),
            "badge_tone": tones[o.status],
            "avatar": True,
            "link": reverse("admin:shop_order_change", args=[o.pk]),
        })
    return items
```

```python
{"type": "table", "title": "Top products", "data": "shop.dashboard.top_products", "width": 7, "link": "admin:shop_product_changelist"},
{"type": "list", "title": "Latest orders", "items": "shop.dashboard.latest_orders", "width": 5, "link": "admin:shop_order_changelist"},
```

## 6. Stacked bars and progress bars

```python
def channels(request):
    start = (timezone.localdate().replace(day=1) - datetime.timedelta(days=150)).replace(day=1)
    rows = (
        Order.objects.filter(created_at__date__gte=start)
        .annotate(m=TruncMonth("created_at"))
        .values("m", "channel")
        .annotate(n=Count("id"))
        .order_by("m")
    )
    months = sorted({r["m"].date() if hasattr(r["m"], "date") else r["m"] for r in rows})
    series = []
    for key, name in Order.Channel.choices:
        values = [sum(r["n"] for r in rows if r["channel"] == key and (r["m"].date() if hasattr(r["m"], "date") else r["m"]) == m) for m in months]
        series.append({"name": name, "values": values})
    return {"labels": [m.strftime("%b") for m in months], "series": series}


def category_share(request):
    rows = (
        OrderItem.objects.filter(order__status__in=PAID)
        .values("product__category__name")
        .annotate(v=Sum(F("quantity") * F("unit_price")))
        .order_by("-v")[:5]
    )
    total = sum(float(r["v"]) for r in rows) or 1
    tones = ["accent", "info", "success", "warning", "neutral"]
    return [
        {"label": r["product__category__name"], "value": float(r["v"]), "total": total, "display": f"${float(r['v']):,.0f}", "tone": tones[i % 5]}
        for i, r in enumerate(rows)
    ]
```

```python
{"type": "chart", "kind": "stacked-bar", "title": "Orders by channel", "subtitle": "Last six months", "data": "shop.dashboard.channels", "width": 7, "height": 220},
{"type": "progress", "title": "Revenue by category", "items": "shop.dashboard.category_share", "width": 5},
```

## 7. A year of activity, retention and fulfilment

```python
def order_days(request):
    start = timezone.localdate() - datetime.timedelta(days=370)
    rows = Order.objects.filter(created_at__date__gte=start).annotate(d=TruncDate("created_at")).values("d").annotate(n=Count("id"))
    return {r["d"]: r["n"] for r in rows}
```

```python
{"type": "heatmap", "title": "Order activity", "subtitle": "Orders per day, last twelve months", "data": "shop.dashboard.order_days", "unit": "orders", "weeks": 52, "width": 12},
{"type": "contributions", "title": "Your activity", "icon": "activity", "weeks": 30, "width": 8},
{"type": "team", "title": "Team", "icon": "users", "days": 30, "width": 4},
{"type": "cohort", "title": "Customer retention", "subtitle": "Share of new customers who ordered again, by signup month", "data": "shop.dashboard.retention", "width": 12},
{"type": "tracker", "title": "Fulfilment", "subtitle": "Last 60 days", "data": "shop.dashboard.fulfilment", "width": 12},
{"type": "activity", "title": "Recent changes", "width": 6, "limit": 6},
{"type": "recent", "title": "Recently opened", "width": 6},
```

The `retention` and `fulfilment` functions are longer; they are in `example/shop/dashboard.py` in the repository. `retention` returns rows of `{"label", "sub", "total", "values"}` and `fulfilment` returns one tracker row with a tone per day.

## 8. Badges that follow the same numbers

The two numbers people check most also go on the sidebar:

```python
def pending_orders(request):
    return Order.objects.filter(status="pending").count()


def low_stock(request):
    return Product.objects.filter(stock__lt=15, status="active").count()
```

```python
"SIDEBAR": {
    "navigation": [
        {"title": "Store", "items": [
            {"title": "Orders", "icon": "receipt", "link": "admin:shop_order_changelist", "badge": "shop.dashboard.pending_orders", "badge_variant": "warning"},
            {"title": "Products", "icon": "package", "link": "admin:shop_product_changelist", "badge": "shop.dashboard.low_stock", "badge_variant": "danger"},
        ]},
    ],
},
```

## 9. Make it live

The dashboard already refreshes with the default polling transport. For changes to show up within a second or two, switch to Server-Sent Events and give the processes a shared cache:

```python
CC_ADMIN = {
    "LIVE": {"transport": "sse", "interval": 4, "dashboard_interval": 15},
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    },
}
```

Now open the dashboard and, in a second terminal, place orders:

```bash
python manage.py simulate --every 3
```

Every few seconds the order count changes, the "Orders" badge goes up, a popup announces the order, and the dashboard redraws its cards at most once every 15 seconds.

## 10. Keep it quick

With every widget, sidebar badges, the notification bell and the session, the example dashboard runs about fifty queries per page load. That is fine for a handful of staff. On a busy shop, cache the heavier functions:

```python
from django.core.cache import cache


def order_days(request):
    found = cache.get("dash:order_days")
    if found is None:
        start = timezone.localdate() - datetime.timedelta(days=370)
        rows = Order.objects.filter(created_at__date__gte=start).annotate(d=TruncDate("created_at")).values("d").annotate(n=Count("id"))
        found = {r["d"]: r["n"] for r in rows}
        cache.set("dash:order_days", found, 300)
    return found
```

A year of daily counts does not need to be exact to the second, so five minutes of caching costs nothing in usefulness.
