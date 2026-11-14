# Command palette

Press {kbd}`Ctrl+K` (or {kbd}`⌘+K` on a Mac), or click the search box in the top bar, and a palette opens over the page. Type a few letters and pick a result with the arrow keys and {kbd}`Enter`. {kbd}`Ctrl+Enter` opens the result in a new tab.

```{image} ../screenshots/command-palette.jpg
:alt: The command palette showing records that match "leyla"
```

## What it finds

With nothing typed, the palette shows your recent records and the models you can open. Once you type, it searches everything below:

| Group | Contents |
| --- | --- |
| Recent | The last records you opened. |
| Navigate | Every model you may see, the dashboard, your activity page. |
| Records | Records whose model admin has `search_fields`, found with the admin's own search. |
| Actions | "New order", "New product" and so on, for every model you may add to. |
| Appearance | Every theme, and light, dark and automatic mode. |
| Help | The keyboard shortcuts dialog. |

Record search uses the same `get_search_results()` as the search box of each list, so whatever you set in `search_fields` (including lookups like `customer__email`) works in the palette too. Only models the user may view are searched, and a model admin that raises an error during the search is skipped instead of breaking the palette.

## Settings

```python
CC_ADMIN = {
    "COMMAND_PALETTE": {
        "enabled": True,
        "search_models": True,
        "limit": 5,
        "min_length": 2,
        "commands": [],
        "search_callback": None,
    },
}
```

`enabled`
: Turn the palette off completely with `False`. The search box in the top bar disappears too.

`search_models`
: Search records. With `False` the palette still lists models, actions and themes.

`limit`
: How many records to return per model, from 1 to 25. Default 5.

`min_length`
: How many characters to type before records are searched. Default 2.

`commands`
: Extra entries of your own. See below.

`search_callback`
: A function, or a dotted path, that adds your own search results. See below.

## Your own commands

Commands are fixed entries. They show up once the user starts typing and their title or subtitle matches:

```python
CC_ADMIN = {
    "COMMAND_PALETTE": {
        "commands": [
            {"title": "Weekly reports", "subtitle": "Revenue by channel", "icon": "chart-pie", "link": "admin:shop_order_reports"},
            {"title": "Pending orders", "subtitle": "Orders waiting for payment", "icon": "clock", "link": "/admin/shop/order/?status__in=pending"},
            {"title": "Grafana", "icon": "activity", "link": "https://grafana.example.com/", "keywords": "metrics graphs", "group": "Tools", "permission": "superuser"},
        ],
    },
}
```

| Key | Meaning |
| --- | --- |
| `title` | The text of the entry. |
| `subtitle` | A second line. |
| `icon` | A Lucide icon. Defaults to an arrow. |
| `link` | A URL name, a path or a full URL. |
| `keywords` | Extra words that should find this entry. They take the place of the subtitle, so they only count for entries without a `subtitle`. |
| `group` | The group heading. Defaults to "Commands". |
| `permission` | Who sees the entry. See [Permissions](permissions.md). |

Each command may also be a callable that takes the request and returns the dict, or `None` to skip it.

## Searching your own data

`search_callback` receives the request and the text typed so far, and returns a list of results. They are shown above the record results:

```python
from django.urls import reverse

from .models import Order


def palette(request, query):
    if query.upper().startswith("NW-"):
        order = Order.objects.filter(number__iexact=query).first()
        if order:
            return [{
                "title": f"Order {order.number}",
                "subtitle": f"{order.customer} · ${order.total}",
                "icon": "receipt",
                "link": reverse("admin:shop_order_change", args=[order.pk]),
            }]
    return []
```

```python
CC_ADMIN = {"COMMAND_PALETTE": {"search_callback": "shop.search.palette"}}
```

Each result takes `title`, `subtitle`, `icon` and `link`. The callback runs on every keystroke after `min_length`, so keep it quick. At most 60 results are returned in total.
