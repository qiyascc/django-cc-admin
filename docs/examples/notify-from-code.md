# Recipe: telling staff about changes

This recipe covers the usual ways a back office tells people that something happened: a rule for every new order, a message from your own code when a payment fails, a nightly summary from a scheduled job, and a personal note when a task is assigned to someone.

## 1. Every new order, with a rule

No code at all, only settings:

```python
CC_ADMIN = {
    "NOTIFICATIONS": {
        "rules": [
            {
                "model": "shop.order",
                "on": "created",
                "title": "New order {obj.number}",
                "body": "{obj.customer} · ${obj.total}",
                "level": "success",
                "icon": "receipt",
                "sound": "cash",
            },
        ],
    },
}
```

Every active staff user gets it, except the person who created the order in the admin. The link goes to the order's edit page.

## 2. Only when a status changes

A rule on `"updated"` runs on every save. Remember the old status when the order is loaded, and compare in `when`:

```python
class Order(models.Model):
    @classmethod
    def from_db(cls, db, field_names, values):
        obj = super().from_db(db, field_names, values)
        obj.tracker_status = obj.__dict__.get("status")
        return obj
```

```python
def refunded(order, event):
    return order.status == "refunded" and getattr(order, "tracker_status", None) != "refunded"
```

```python
{
    "model": "shop.order",
    "on": "updated",
    "when": "shop.notifications.refunded",
    "title": "{obj.number} was refunded",
    "body": "{obj.customer} · ${obj.total}",
    "level": "danger",
    "icon": "undo-2",
    "to": "superuser",
},
```

The same pattern works for stock falling under a limit:

```python
def low_stock(product, event):
    return 0 < product.stock < 5 and getattr(product, "tracker_stock", 0) >= 5
```

## 3. From your own code: a failed payment

When the event does not map to a model save, call `notify()` where it happens, for example in a payment webhook:

```python
from cc_admin.notify import notify


def payment_webhook(request):
    event = parse_webhook(request)
    if event.type == "payment_failed":
        order = Order.objects.get(number=event.order_number)
        notify(
            ["perm:shop.change_order", "group:Support"],
            f"Payment failed for {order.number}",
            body=f"{order.customer} · {event.reason}",
            link=f"/admin/shop/order/{order.pk}/change/",
            level="danger",
            icon="credit-card",
            sound="alert",
            key=f"payment-failed:{order.pk}",
            data={"order": order.pk, "reason": event.reason},
        )
    return HttpResponse(status=204)
```

`parse_webhook` stands for your payment provider's code. Superusers, everyone with change permission on orders and the Support group are told. The `key` makes sure a second failure for the same order replaces the first push on people's phones instead of adding another.

## 4. To one person: an assignment

```python
def assign(order, user, by):
    order.assigned_to = user
    order.save(update_fields=["assigned_to"])
    notify(
        user,
        f"{order.number} was assigned to you",
        body=f"From {by.get_full_name() or by.get_username()}",
        link=f"/admin/shop/order/{order.pk}/change/",
        level="accent",
        icon="user-check",
        actor=by,
    )
```

Passing `actor` shows who sent it.

## 5. From a scheduled job: a nightly summary

`notify()` works the same outside a request, for example in a management command run by cron:

```python
import datetime

from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone

from cc_admin.notify import notify, send_push
from shop.models import Order


class Command(BaseCommand):
    help = "Send yesterday's numbers to the managers."

    def handle(self, *args, **options):
        day = timezone.localdate() - datetime.timedelta(days=1)
        orders = Order.objects.filter(created_at__date=day)
        total = orders.aggregate(s=Sum("total"))["s"] or 0
        created = notify(
            "group:Managers",
            f"{orders.count()} orders yesterday",
            body=f"${total:,.2f} in total.",
            link="/admin/",
            level="info",
            icon="chart-line",
            push=False,
        )
        if created:
            send_push([n.recipient_id for n in created], created[0])
```

`notify()` normally sends push messages in a background thread so a web request does not wait. A management command can end before that thread is done, so here push is switched off in `notify()` and `send_push()` is called directly, which waits until every message is sent.

```text
0 7 * * * cd /srv/shop && .venv/bin/python manage.py daily_summary
```

## 6. Marking things read from code

When a notification is about a task and the task is done somewhere else, mark it read for the person who did it:

```python
from cc_admin.models import Notification
from cc_admin.notify import mark_read

ids = list(Notification.objects.filter(recipient=user, key=f"payment-failed:{order.pk}", read_at__isnull=True).values_list("pk", flat=True))
mark_read(user, ids)
```

Their bell updates on its own.

## 7. Keep the table small

Add the cleanup to cron next to your other jobs:

```text
30 3 * * 0 cd /srv/shop && .venv/bin/python manage.py cc_admin_cleanup
```

It deletes notifications older than `NOTIFICATIONS["keep_days"]`, 60 days by default.
