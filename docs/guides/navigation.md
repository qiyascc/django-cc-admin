# Sidebar, tabs and icons

Without any settings the menu lists every app and model the user may see, with an icon guessed from each model's name. This page shows how to put your own groups at the top, add badges with live counts, set icons, and show a row of tabs above related lists.

## The default menu

With no settings at all, the menu has:

- a filter box at the top that narrows the menu as you type,
- "Dashboard" and, if the activity pages are on, "Activity",
- one group per app, with the models the user has permission to see,
- a star next to each list title, to pin that model to the top of the menu.

Models without an icon get one guessed from their name. `Order`, `Invoice` and `Receipt` get a receipt, `Product`, `Item` and `Stock` get a package, `Customer` and `Client` get a person, `Payment` and `Refund` get a credit card, and so on for about thirty families of names. Anything unknown gets a box.

## Settings

```python
CC_ADMIN = {
    "SIDEBAR": {
        "search": True,
        "show_all_applications": True,
        "pinned": True,
        "icons": {"shop.category": "folder-tree", "shop": "shopping-bag"},
        "navigation": [],
    },
}
```

`search`
: Show the filter box. Default `True`.

`show_all_applications`
: List every app and model after your own groups. Models you already placed in a group are not repeated. Set it to `False` to show only your own groups. Default `True`.

`pinned`
: Allow pinning models with the star. Pins are kept in the browser. Default `True`.

`icons`
: Icons for models (`"app_label.modelname"`) and for apps (`"app_label"`), overriding the guesses.

`navigation`
: Your own groups, described below.

## Your own groups

```python
CC_ADMIN = {
    "SIDEBAR": {
        "navigation": [
            {
                "title": "Store",
                "icon": "store",
                "collapsible": False,
                "items": [
                    {
                        "title": "Orders",
                        "icon": "receipt",
                        "link": "admin:shop_order_changelist",
                        "badge": "shop.dashboard.pending_orders",
                        "badge_variant": "warning",
                    },
                    {
                        "title": "Products",
                        "icon": "package",
                        "link": "admin:shop_product_changelist",
                        "badge": "shop.dashboard.low_stock",
                        "badge_variant": "danger",
                    },
                    {"title": "Customers", "icon": "users", "link": "admin:shop_customer_changelist"},
                    {"title": "Reports", "icon": "chart-pie", "link": "admin:shop_order_reports"},
                ],
            },
            {
                "title": "Finance",
                "permission": "group:Accounting",
                "items": [
                    {"title": "Invoices", "icon": "file-text", "link": "admin:billing_invoice_changelist"},
                    {"title": "Stripe dashboard", "icon": "external-link", "link": "https://dashboard.stripe.com/"},
                ],
            },
        ],
    },
}
```

### Group keys

| Key | Meaning |
| --- | --- |
| `title` | The group heading. |
| `icon` | Shown next to the heading in the themes that display group icons. Defaults to `layers`. |
| `items` | The links in the group. A group with no visible items is hidden. |
| `collapsible` | Let users fold the group. Default `False`. App groups added by `show_all_applications` are always collapsible. |
| `permission` | Who sees the group. See [Permissions](permissions.md). |
| `key` | A stable name used to remember whether the group is folded. Defaults to the title in lowercase with dashes. |

A group can also be a callable that takes the request and returns the dict, or `None` to hide it.

### Item keys

| Key | Meaning |
| --- | --- |
| `title` | The text. |
| `icon` | A Lucide icon name. Defaults to a dot. |
| `link` | A URL name, a path or a full URL. Full URLs are marked as external. |
| `badge` | A number or short text shown on the right. See below. |
| `badge_variant` | The tone of the badge: `accent` (default), `neutral`, `info`, `success`, `warning` or `danger`. |
| `permission` | Who sees the item. |
| `active` | Force the item to look selected: `True`, `False` or a callable that takes the request. Normally the item whose link best matches the current address is selected on its own. |

## Badges

A badge can be a plain value, a callable that takes the request, or a dotted path to such a function:

```python
def pending_orders(request):
    return Order.objects.filter(status="pending").count()
```

```python
{"title": "Orders", "link": "admin:shop_order_changelist", "badge": "shop.dashboard.pending_orders"}
```

A badge that comes out as `0`, `None` or an empty string is hidden, so you can return the count directly without checking for zero yourself.

While a page is open, live updates keep the badges in sync: when an order is placed somewhere else, the count next to "Orders" changes without a reload. This uses the same channel as the rest of the [live updates](live-updates.md) and can be turned off with `"LIVE": {"badges": False}`.

```{note}
A badge value that is a string containing a dot is treated as a dotted path and imported. For a fixed label, use text without dots, like `"new"` or `"beta"`.
```

Badge functions run on every page and every time live updates refresh the badges, so keep them cheap: a `count()` on an indexed column is fine, a large aggregation is not. Cache the result if needed.

## Tabs above a list

Tabs show a row of links above the pages of one or more models. They work well for saved views of the same list:

```python
CC_ADMIN = {
    "TABS": [
        {
            "models": ["shop.order"],
            "items": [
                {"title": "All orders", "link": "/admin/shop/order/"},
                {"title": "Pending", "link": "/admin/shop/order/?status__in=pending", "badge": "shop.dashboard.pending_orders"},
                {"title": "Shipped", "link": "/admin/shop/order/?status__in=shipped"},
                {"title": "Refunds", "link": "/admin/shop/order/?status__in=refunded"},
            ],
        },
    ],
}
```

The tabs appear on the list, add and edit pages of every model in `models` (written as `"app_label.modelname"`). Instead of, or as well as, `models`, you can give `pages`: a list of paths or URL names, and the tabs appear on every page whose address starts with one of them. That is how you put tabs on a [custom page](custom-pages.md).

Items take `title`, `icon`, `link`, `badge`, `permission` and `active`, like sidebar items. A tab is marked active when the current address, including the query string, is exactly its link.

When several tab groups match a page, only the first one in the list is shown.

## Icons

Icons everywhere in django-cc-admin are [Lucide](https://lucide.dev/icons) icons, bundled as one SVG sprite of more than two thousand symbols. Only the icons a page uses are sent with that page.

A name that is not in the bundled set is replaced by a small dot. Lucide renames icons from time to time, and the bundled set uses the names from when the package was built. If an icon from the Lucide website does not show up, check the names that ship with your version:

```python
from cc_admin import icons

icons.exists("triangle-exclamation-point")
sorted(name for name in icons.symbols() if "triangle" in name)
```

In your own templates use the `icon` tag:

```django
{% load cc_admin %}
{% icon "package" %}
{% icon "triangle-exclamation-point" "my-class" "Warning" %}
```

The second argument adds a CSS class and the third gives the icon an accessible label.
