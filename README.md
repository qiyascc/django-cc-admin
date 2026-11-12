# django-cc-admin

A new skin and a set of tools for the Django admin. It replaces the default look with one of fifteen themes, builds the dashboard from your settings, adds a command palette, keyboard shortcuts, better filters, row and page actions, CSV and JSON export, and a lot of small things the stock admin never had.

Your existing `ModelAdmin` classes keep working. Swap in `cc_admin.admin.ModelAdmin` only where you want the extra features.

Works with Django 5.0, 5.1, 5.2, 6.0 and 6.1, Python 3.10 and up.

![Dashboard, Aurora theme](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/dashboard.jpg)

## Install

```bash
pip install django-cc-admin
```

Put `cc_admin` above `django.contrib.admin`:

```python
INSTALLED_APPS = [
    "cc_admin",
    "django.contrib.admin",
    ...
]
```

That is all you need. Open `/admin/` and you get the new look, the palette and the theme switcher. A system check tells you if the app order is wrong.

## Themes

| Theme | Layout | Modes | Feel |
|---|---|---|---|
| `aurora` | sidebar | light, dark | Clean indigo, the default |
| `midnight` | sidebar | dark | Deep navy with a cyan edge |
| `paper` | top bar | light, dark | Serif headings on warm paper |
| `terminal` | icon rail | dark | Green phosphor, monospace everywhere |
| `nord` | sidebar | light, dark | The Nord palette |
| `brutal` | top bar | light | Thick borders and hard shadows |
| `glass` | floating | dark, light | Frosted panels over a soft glow |
| `slate` | sidebar | light, dark | Dense, dark menu, built for long tables |
| `sunset` | floating | light, dark | Coral gradient menu |
| `forest` | sidebar | light, dark | Moss green, Fraunces titles |
| `mono` | top bar | light, dark | Black and white only |
| `rose` | floating | light, dark | Pink, round corners, pill buttons |
| `ocean` | icon rail | light, dark | Deep teal |
| `classic` | sidebar | light | A desktop from 1995 |
| `cc` | sidebar | dark, light | Ink and ice blue, from theqiyas.cc |

Every user can pick a theme, mode (auto, light, dark) and density (compact, default, roomy) from the user menu or by pressing `t`. The choice is kept in a cookie, so the page renders in the right theme with no flash. Turn the switcher off with `THEME_SWITCHER: False` to force one theme for everybody.

All fonts and icons ship with the package. Nothing is loaded from a CDN.

### Screenshots

Each picture shows the dashboard, the order list and a product form.

| | |
|---|---|
| **Aurora** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/aurora-light.jpg) | **Midnight** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/midnight-dark.jpg) |
| **Paper** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/paper-light.jpg) | **Terminal** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/terminal-dark.jpg) |
| **Nord** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/nord-light.jpg) | **Brutal** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/brutal-light.jpg) |
| **Glass** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/glass-dark.jpg) | **Slate** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/slate-light.jpg) |
| **Sunset** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/sunset-light.jpg) | **Forest** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/forest-light.jpg) |
| **Mono** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/mono-light.jpg) | **Rose** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/rose-light.jpg) |
| **Ocean** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/ocean-light.jpg) | **Classic** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/classic-light.jpg) |
| **CC** ![](https://raw.githubusercontent.com/qiyascc/django-cc-admin/main/docs/screenshots/cc-dark.jpg) | |

## Settings

Everything lives in one dict. All keys are optional.

```python
CC_ADMIN = {
    "SITE_HEADER": "Northwind",
    "SITE_SUBHEADER": "Store admin",
    "SITE_TITLE": "Northwind admin",
    "SITE_URL": "/",
    "SITE_LOGO": {"light": "img/logo-dark.svg", "dark": "img/logo-light.svg"},
    "SITE_ICON": "img/icon.svg",
    "SITE_FAVICON": "img/favicon.png",

    "THEME": "aurora",
    "THEME_SWITCHER": True,
    "COLOR_SCHEME": "auto",
    "DENSITY": "comfortable",
    "LAYOUT": None,
    "FONTS": True,

    "TOKENS": {"accent": "#e11d48", "radius": "6px", "dark": {"accent": "#fb7185"}},
    "THEMES": {
        "acme": {"extends": "midnight", "label": "Acme", "tokens": {"accent": "#f97316"}},
    },

    "ENVIRONMENT": ("Staging", "warning"),
    "STYLES": ["css/admin-extra.css"],
    "SCRIPTS": ["js/admin-extra.js"],
    "USER_LINKS": [{"title": "Store front", "icon": "store", "link": "/"}],
    "FOOTER": None,

    "SIDEBAR": {...},
    "TABS": [...],
    "DASHBOARD": {...},
    "COMMAND_PALETTE": {"enabled": True, "search_models": True, "limit": 5, "min_length": 2},
    "SHORTCUTS": True,
    "LOGIN": {"title": "Run the whole store from one place.", "text": "...", "image": "img/login.jpg"},
    "LIST_EXPORT": True,
    "WARN_UNSAVED_FORMS": True,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
}
```

Any value can be a callable that takes the request. Callbacks such as badges, permissions and dashboard data can also be given as a dotted path, like `"shop.dashboard.revenue"`.

Links accept a URL name (`"admin:shop_order_changelist"`), a path, or a full URL.

`LAYOUT` forces one of `sidebar`, `topbar`, `rail` or `float` for every theme. `TOKENS` overrides the CSS variables behind the themes, so `{"accent": "#e11d48"}` becomes `--cc-accent`. Look at the top of `cc_admin/static/cc_admin/css/cc.css` for the full list.

### Sidebar

```python
"SIDEBAR": {
    "search": True,
    "show_all_applications": True,
    "pinned": True,
    "icons": {"shop.category": "folder-tree", "shop": "shopping-bag"},
    "navigation": [
        {
            "title": "Store",
            "collapsible": False,
            "items": [
                {
                    "title": "Orders",
                    "icon": "receipt",
                    "link": "admin:shop_order_changelist",
                    "badge": "shop.dashboard.pending_orders",
                    "badge_variant": "warning",
                    "permission": lambda request: request.user.has_perm("shop.view_order"),
                },
            ],
        },
    ],
},
```

Icons are [Lucide](https://lucide.dev/icons) names. Models without an icon get one guessed from their name, so `Order` gets a receipt and `Customer` gets a person. Users can pin any model to the top of the menu with the star next to its title.

### Tabs

Show a row of tabs above the pages of some models:

```python
"TABS": [
    {
        "models": ["shop.order"],
        "items": [
            {"title": "All orders", "link": "/admin/shop/order/"},
            {"title": "Pending", "link": "/admin/shop/order/?status__in=pending", "badge": "shop.dashboard.pending_orders"},
            {"title": "Refunds", "link": "/admin/shop/order/?status__in=refunded"},
        ],
    },
],
```

### Dashboard

The dashboard is a twelve column grid of widgets. Each widget picks its data from a value, a callable or a dotted path.

```python
"DASHBOARD": {
    "subtitle": "Here is how the store did over the last 30 days.",
    "callback": "shop.dashboard.context",
    "widgets": [
        {"type": "kpi", "title": "Revenue", "icon": "wallet", "value": "shop.dashboard.revenue"},
        {"type": "chart", "kind": "area", "title": "Revenue", "data": "shop.dashboard.revenue_chart", "prefix": "$", "width": 8},
        {"type": "chart", "kind": "donut", "title": "Order status", "data": "shop.dashboard.status_split", "width": 4},
        {"type": "table", "title": "Top products", "data": "shop.dashboard.top_products", "width": 7},
        {"type": "list", "title": "Latest orders", "items": "shop.dashboard.latest_orders", "width": 5},
        {"type": "heatmap", "title": "Order activity", "data": "shop.dashboard.order_days", "weeks": 52},
        {"type": "activity", "title": "Recent changes", "width": 6},
        {"type": "recent", "title": "Recently opened", "width": 6},
    ],
},
```

| Type | Data it expects |
|---|---|
| `kpi` | `value`: a number, or a dict with `value`, `delta` (percent), `delta_label`, `spark` (list of numbers), `prefix`, `suffix` |
| `chart` | `kind` is `line`, `area`, `stacked-area`, `bar`, `stacked-bar` or `donut`. Line and bar take `{"labels": [...], "series": [{"name": ..., "values": [...]}]}`. Donut takes `[{"label": ..., "value": ..., "color": ...}]` |
| `table` | `{"headers": [...], "rows": [[cell, ...]], "align": ["", "right"]}`. A cell is text or a dict with `text`, `sub`, `link`, `badge` |
| `list` | items with `title`, `subtitle`, `meta`, `link`, `icon`, `avatar`, `badge`, `badge_tone` |
| `progress` | items with `label`, `value`, `total`, `display`, `tone` |
| `links` | items with `title`, `text`, `icon`, `link` |
| `heatmap` | a dict of `date: count` |
| `models` | `models`: a list like `["shop.order"]`, or nothing for every model. Shows counts |
| `activity` | the admin log. `scope` is `all` or `mine`, `limit` sets the length |
| `recent` | records the user opened lately. Kept in the browser |
| `note` | `text` and `tone` |
| `html` | `template` plus an optional `context` callable, or `html` |

Every widget also takes `title`, `subtitle`, `icon`, `width` (1 to 12), `link`, `link_text` and `permission`. Charts are plain SVG drawn on the server and pick their colours from the theme.

## ModelAdmin

```python
from cc_admin.admin import ModelAdmin, StackedInline, TabularInline
from cc_admin.decorators import action, display
from cc_admin.filters import ChoicesCheckboxFilter, RangeDateFilter, RangeNumericFilter, RelatedDropdownFilter


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["number", "customer_card", "status_badge", "total"]
    list_filter = [("status", ChoicesCheckboxFilter), ("total", RangeNumericFilter), ("created_at", RangeDateFilter)]
    actions_list = ["sync"]
    actions_row = ["refund"]
    actions_detail = ["print_invoice"]
    actions_submit_line = ["save_and_notify"]
    conditional_fields = {"gift_message": "is_gift", "tracking_code": "status in ['shipped', 'delivered']"}
    list_export = True
    compressed_fields = False
    warn_unsaved_form = True

    @display(description="Customer", header=True)
    def customer_card(self, obj):
        return obj.customer.name, obj.customer.email

    @display(description="Status", label={"paid": "info", "shipped": "accent", "refunded": "danger"})
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()

    @action(description="Refund", icon="undo-2", variant="danger", confirm="Refund this order?")
    def refund(self, request, obj):
        ...

    @action(description="Sync with warehouse", icon="refresh-cw")
    def sync(self, request):
        ...
```

What you get:

- `actions_list` are buttons next to "Add". They get `(request)`.
- `actions_row` show up in a menu at the end of each row. They get `(request, obj)`.
- `actions_detail` are buttons at the top of the edit page. They get `(request, obj)`.
- `actions_submit_line` are extra buttons in the save bar. They run after the object is saved and get `(request, obj)`.
- Any action can return a response. If it returns nothing the user goes back where they came from.
- `@action` takes `description`, `icon`, `variant` (`default`, `primary`, `danger`, `success`, `warning`, `info`), `confirm`, `permissions`, `url_path` and `new_tab`.
- `@display` adds `label` (a badge, with a dict mapping values to tones), `header` (title, subtitle and an avatar), `copy` (a copy button), `mono` and `tags` on top of Django's own options.
- `conditional_fields` hides a field until an expression over other fields is true. Expressions support `==`, `!=`, `<`, `>`, `in`, `and`, `or`, `not`, lists and literals.
- Fieldsets with the class `"tab"` become tabs. Fieldsets with `"sidebar"` go into a sticky column on the right. `"collapse"` still works.
- Inlines take `tab = True`, `collapsible = True`, `hide_title = True`, and `ordering_field = "position"` for drag and drop sorting.
- The list gets "Export selected to CSV/JSON" actions and an Export menu for the current filtered view. Set `list_export = False` to turn it off.
- `compressed_fields = True` puts labels to the left of the inputs.

### Filters

| Filter | Use |
|---|---|
| `FieldTextFilter` | Contains search on one field: `("country", FieldTextFilter)` |
| `FieldExactFilter` | Exact match on one field |
| `TextFilter` | Subclass it, set `parameter_name`, write `queryset()` |
| `RangeNumericFilter` | From and to inputs for numbers |
| `RangeDateFilter` | From and to dates, works on DateField and DateTimeField |
| `RangeDateTimeFilter` | From and to with time |
| `ChoicesCheckboxFilter` | Pick several choices at once |
| `RelatedCheckboxFilter` | Pick several related objects at once |
| `ChoicesDropdownFilter`, `RelatedDropdownFilter`, `AllValuesDropdownFilter`, `DropdownFilter` | A select instead of a long list |
| `BooleanRadioFilter` | Yes, No, All as one segmented control |

Filters live in a side panel. Active filters show as chips above the table, each with its own remove button.

## Keyboard

| Keys | Does |
|---|---|
| `Ctrl K` / `⌘ K` | Command palette: jump to any model, open records found by search, add new records, switch themes |
| `/` | Focus the search box |
| `g d` | Go to the dashboard |
| `t` | Theme panel |
| `[` | Collapse the menu |
| `j` `k` | Move between rows |
| `x` | Select the row |
| `Enter` `o` | Open the row |
| `n` | Add new |
| `f` | Open filters |
| `←` `→` | Previous and next page |
| `Ctrl S` | Save and keep editing |
| `Ctrl Enter` | Save |
| `?` | All shortcuts |

The palette searches every registered model that has `search_fields`, and only shows records the user can view.

## Also in the box

- Column picker on every list, remembered per model.
- Bulk actions in a floating bar that appears when rows are selected.
- Toasts for messages.
- A warning before leaving a form with unsaved changes.
- Recently opened records in the palette and on the dashboard.
- Environment badge, so nobody confuses staging with production.
- Restyled date pickers, related object buttons, `filter_horizontal` and autocomplete fields.
- Works inside admin popups.
- CSP nonces are passed through when Django provides them.

## Example project

```bash
git clone https://github.com/qiyascc/django-cc-admin
cd django-cc-admin/example
pip install django
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Log in with `admin` / `admin`. The example shop uses most of the features above. `CC_THEME=terminal python manage.py runserver` starts it in another theme.

## Development

```bash
python runtests.py
python scripts/build_themes.py
```

Themes are defined in `scripts/build_themes.py`, which writes `cc_admin/static/cc_admin/css/themes.css`.

## Links

- Source: [github.com/qiyascc/django-cc-admin](https://github.com/qiyascc/django-cc-admin)
- Author: [Qiyas Sadıqov](https://theqiyas.cc), more projects at [theqiyas.cc](https://theqiyas.cc)

## License

MIT. Bundled icons are from Lucide (ISC) and fonts are under the SIL Open Font License. See `NOTICE`.
