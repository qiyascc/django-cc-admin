###############
# Qiyas Sadıqov CC
###############

import datetime
from decimal import Decimal

from django.db.models import Count, F, Sum
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


def revenue(request):
    now, before = _revenue(*_window(30)), _revenue(*_window(30, 30))
    return {"value": now, "prefix": "$", "delta": _change(now, before), "delta_label": "vs last 30 days", "spark": _daily(30)}


def orders(request):
    start, end = _window(30)
    p_start, p_end = _window(30, 30)
    now = Order.objects.filter(created_at__gte=start, created_at__lt=end).count()
    before = Order.objects.filter(created_at__gte=p_start, created_at__lt=p_end).count()
    return {"value": now, "delta": _change(now, before), "delta_label": "vs last 30 days", "spark": _daily(30, "count")}


def average_order(request):
    start, end = _window(30)
    qs = Order.objects.filter(status__in=PAID, created_at__gte=start, created_at__lt=end)
    n = qs.count() or 1
    value = (qs.aggregate(s=Sum("total"))["s"] or 0) / n
    p_start, p_end = _window(30, 30)
    pq = Order.objects.filter(status__in=PAID, created_at__gte=p_start, created_at__lt=p_end)
    before = (pq.aggregate(s=Sum("total"))["s"] or 0) / (pq.count() or 1)
    totals, counts = _daily(30), _daily(30, "count")
    spark = [t / c if c else 0 for t, c in zip(totals, counts)]
    return {"value": value, "prefix": "$", "delta": _change(value, before), "delta_label": "vs last 30 days", "spark": spark}


def new_customers(request):
    start, end = _window(30)
    p_start, p_end = _window(30, 30)
    now = Customer.objects.filter(joined_at__gte=start, joined_at__lt=end).count()
    before = Customer.objects.filter(joined_at__gte=p_start, joined_at__lt=p_end).count()
    first = timezone.localdate() - datetime.timedelta(days=29)
    rows = Customer.objects.filter(joined_at__date__gte=first).annotate(d=TruncDate("joined_at")).values("d").annotate(n=Count("id"))
    found = {r["d"]: r["n"] for r in rows}
    spark = [found.get(first + datetime.timedelta(days=i), 0) for i in range(30)]
    return {"value": now, "delta": _change(now, before), "delta_label": "vs last 30 days", "spark": spark}


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
    return {"labels": labels, "series": [{"name": "This period", "values": current}, {"name": "Previous period", "values": previous, "color": "var(--cc-chart-muted, var(--cc-border-strong))"}]}


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
    labels = [m.strftime("%b") for m in months]
    series = []
    for key, name in Order.Channel.choices:
        values = []
        for m in months:
            values.append(sum(r["n"] for r in rows if r["channel"] == key and (r["m"].date() if hasattr(r["m"], "date") else r["m"]) == m))
        series.append({"name": name, "values": values})
    return {"labels": labels, "series": series}


def status_split(request):
    rows = Order.objects.values("status").annotate(n=Count("id")).order_by("-n")
    names = dict(Order.Status.choices)
    colors = {"delivered": "var(--cc-success)", "shipped": "var(--cc-accent)", "paid": "var(--cc-info)", "pending": "var(--cc-warning)", "refunded": "var(--cc-text-3)", "cancelled": "var(--cc-danger)"}
    return [{"label": names[r["status"]], "value": r["n"], "color": colors.get(r["status"])} for r in rows]


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
        out.append(
            [
                {"text": r["product__name"], "sub": r["product__category__name"], "link": reverse("admin:shop_product_change", args=[r["product__id"]])},
                {"text": f"{r['units']:,}"},
                {"text": f"${r['revenue']:,.0f}"},
                {"text": "Low" if stock < 15 else "OK", "badge": "danger" if stock < 15 else "success"},
            ]
        )
    return {"headers": ["Product", "Units", "Revenue", "Stock"], "rows": out, "align": ["", "right", "right", "right"]}


def latest_orders(request):
    tones = {"pending": "warning", "paid": "info", "shipped": "accent", "delivered": "success", "refunded": "neutral", "cancelled": "danger"}
    items = []
    for o in Order.objects.select_related("customer")[:6]:
        items.append(
            {
                "title": o.customer.name,
                "subtitle": f"{o.number} · {o.get_channel_display()}",
                "meta": f"${o.total:,.2f}",
                "badge": o.get_status_display(),
                "badge_tone": tones[o.status],
                "avatar": True,
                "link": reverse("admin:shop_order_change", args=[o.pk]),
            }
        )
    return items


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


def order_days(request):
    start = timezone.localdate() - datetime.timedelta(days=370)
    rows = Order.objects.filter(created_at__date__gte=start).annotate(d=TruncDate("created_at")).values("d").annotate(n=Count("id"))
    return {r["d"]: r["n"] for r in rows}


def low_stock(request):
    return Product.objects.filter(stock__lt=15, status="active").count()


def pending_orders(request):
    return Order.objects.filter(status="pending").count()
