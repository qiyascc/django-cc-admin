# Actions

Django's admin actions work on a selection of rows: tick some rows, pick an action from the menu, press "Go". django-cc-admin keeps those and adds four more places where a button can live, each with its own signature:

| Option | Where the button is | The method receives |
| --- | --- | --- |
| `actions_list` | Next to "Add" at the top of the list | `(request)` |
| `actions_row` | In a "⋯" menu at the end of each row | `(request, obj)` |
| `actions_detail` | At the top of the edit page, next to "History" | `(request, obj)` |
| `actions_submit_line` | In the save bar at the bottom of the form | `(request, obj)`, after the object was saved |

Django's own `actions` still work as before, and the selection bar shows them in a floating bar as soon as you tick a row.

## A complete example

```python
from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import redirect

from cc_admin.admin import ModelAdmin
from cc_admin.decorators import action

from .models import Order


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["number", "customer", "status", "total"]
    actions = ["mark_shipped"]
    actions_list = ["sync", {"title": "Reports", "icon": "file-chart-column", "items": ["stock_report", "price_report"]}]
    actions_row = ["refund", "resend_receipt"]
    actions_detail = ["print_invoice"]
    actions_submit_line = ["save_and_notify"]

    @admin.action(description="Mark selected as shipped")
    def mark_shipped(self, request, queryset):
        count = queryset.update(status="shipped")
        messages.success(request, f"{count} orders marked as shipped.")

    @action(description="Sync with warehouse", icon="refresh-cw")
    def sync(self, request):
        messages.success(request, "Orders synced with the warehouse.")

    @action(description="Stock report", icon="boxes")
    def stock_report(self, request):
        messages.info(request, "Stock report is on its way to your inbox.")

    @action(description="Price history", icon="chart-line")
    def price_report(self, request):
        messages.info(request, "Price history exported.")

    @action(description="Refund", icon="undo-2", variant="danger", confirm="Refund this order?", permissions=["change"])
    def refund(self, request, obj):
        obj.status = "refunded"
        obj.save(update_fields=["status"])
        messages.warning(request, f"{obj.number} refunded.")

    @action(description="Resend receipt", icon="mail")
    def resend_receipt(self, request, obj):
        messages.success(request, f"Receipt sent to {obj.customer.email}.")

    @action(description="Print invoice", icon="printer", new_tab=True)
    def print_invoice(self, request, obj):
        response = HttpResponse(render_invoice_pdf(obj), content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{obj.number}.pdf"'
        return response

    @action(description="Save and email customer", icon="send")
    def save_and_notify(self, request, obj):
        send_update_email(obj)
        messages.success(request, f"Saved. {obj.customer.email} got an update.")
```

`render_invoice_pdf` and `send_update_email` stand for your own code.

## The @action decorator

`cc_admin.decorators.action` wraps Django's `@admin.action` and adds the parts needed to draw a button.

| Argument | Default | Meaning |
| --- | --- | --- |
| `description` | method name | The button text. |
| `icon` | none | A Lucide icon name. |
| `variant` | `"default"` | The button style: `default`, `primary`, `danger`, `success`, `warning` or `info`. |
| `confirm` | none | A question shown before running. The action only runs if the user agrees. |
| `permissions` | none | A list such as `["change"]` or `["delete"]`. See below. |
| `url_path` | method name with dashes | The last part of the action's URL. |
| `new_tab` | `False` | Open the result in a new browser tab. Useful for files and printable pages. |

Plain methods without the decorator work too. They get a label made from the method name and no icon.

## What an action returns

An action may return any `HttpResponse`: a redirect, a file download, a rendered template. If it returns nothing, the user goes back to the page they came from, and any messages you added show up there as toasts.

```python
from django.shortcuts import redirect


@action(description="Duplicate", icon="copy")
def duplicate(self, request, obj):
    copy = Order.objects.get(pk=obj.pk)
    copy.pk = None
    copy.number = f"{obj.number}-COPY"
    copy.save()
    return redirect("admin:shop_order_change", copy.pk)
```

## Permissions

`permissions` works like Django's: each name `X` in the list calls `has_X_permission(request, obj)` on the model admin, and the button is only shown, and the action only runs, if all of them return `True`. The built in names are `add`, `change`, `delete` and `view`. You can add your own:

```python
class OrderAdmin(ModelAdmin):
    actions_row = ["refund"]

    @action(description="Refund", icon="undo-2", variant="danger", permissions=["refund"])
    def refund(self, request, obj):
        ...

    def has_refund_permission(self, request, obj=None):
        return request.user.has_perm("shop.refund_order") and (obj is None or obj.status == "paid")
```

Row and detail actions pass the object, so a permission method can look at it. In the example only paid orders get a "Refund" item.

## Grouping buttons in a dropdown

`actions_list` and `actions_detail` accept a dict in place of a name. It becomes one button that opens a menu:

```python
actions_list = [
    "sync",
    {"title": "Reports", "icon": "file-chart-column", "items": ["stock_report", "price_report"]},
]
```

The dict takes `title`, `icon`, an optional `variant` and `items`. A group whose items are all hidden by permissions is hidden too.

## Buttons in the save bar

`actions_submit_line` adds buttons next to "Save". Pressing one first saves the form as usual, with all of Django's validation, and then calls your method with the saved object. If the form has errors, nothing is called and the errors are shown. If the method returns nothing, the user lands on the edit page of the object.

This works on the add page too, so "Save and send invitation" on a new user form is one line of code.

## How actions are called

All the new action types are sent as `POST` requests with the CSRF token, so they are safe to use for anything that changes data. The URLs are added to each model admin automatically:

```text
/admin/<app>/<model>/cc-action/<url_path>/
/admin/<app>/<model>/<pk>/cc-action/<url_path>/
```

The first is used by `actions_list`, the second by `actions_row` and `actions_detail`. You do not need to add anything to `urls.py`.
