# django-cc-admin

A new skin and a set of tools for the Django admin. It replaces the default look with one of fifteen themes, builds the dashboard from your settings, adds a command palette, keyboard shortcuts you can rebind, a GitHub style activity page for your team, better filters, row and page actions, CSV and JSON export, and a lot of small things the stock admin never had.

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

    "SITE_SYMBOL": "store",
    "SITE_DROPDOWN": [{"title": "Warehouse admin", "icon": "warehouse", "link": "https://warehouse.example.com/admin/"}],

    "THEME": "aurora",
    "THEME_SWITCHER": True,
    "COLOR_SCHEME": "auto",
    "DENSITY": "comfortable",
    "LAYOUT": None,

    "COLORS": {"accent": "#e11d48", "sidebar": "#0f172a", "dark": {"background": "#0b0b0f"}},
    "FONTS": {"body": "Manrope", "heading": "Fraunces", "mono": "JetBrains Mono", "size": 15},
    "RADIUS": "soft",
    "TOKENS": {"side-w": "280px"},
    "THEMES": {
        "acme": {"extends": "midnight", "label": "Acme", "tokens": {"accent": "#f97316"}},
    },
    "APPEARANCE": {"accent": True, "font": True, "font_size": True, "radius": True},

    "ENVIRONMENT": ("Staging", "warning"),
    "ENVIRONMENT_TITLE_PREFIX": True,
    "STYLES": ["css/admin-extra.css"],
    "SCRIPTS": ["js/admin-extra.js"],
    "USER_LINKS": [{"title": "Store front", "icon": "store", "link": "/"}],
    "FOOTER": None,

    "SIDEBAR": {...},
    "TABS": [...],
    "DASHBOARD": {...},
    "COMMAND_PALETTE": {...},
    "SHORTCUTS": {...},
    "ACTIVITY": {...},
    "LOGIN": {"title": "Run the whole store from one place.", "text": "...", "image": "img/login.jpg"},
    "FORMS": {"switches": False, "json_editor": True, "show_cancel": True, "char_counter": True},
    "LIST_EXPORT": True,
    "LIST_PER_PAGE_OPTIONS": [25, 50, 100, 200],
    "WARN_UNSAVED_FORMS": True,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "SHOW_LANGUAGES": False,
}
```

Any value can be a callable that takes the request. Callbacks such as badges, permissions and dashboard data can also be given as a dotted path, like `"shop.dashboard.revenue"`.

Links accept a URL name (`"admin:shop_order_changelist"`), a path, or a full URL.

`LAYOUT` forces one of `sidebar`, `topbar`, `rail` or `float` for every theme.

`SITE_SYMBOL` puts a Lucide icon in the brand square instead of initials. `SITE_DROPDOWN` adds a small menu next to the brand for jumping between sites. `ENVIRONMENT_TITLE_PREFIX` puts the environment name in the browser tab, so `[Staging] Orders` never gets mixed up with production. `SHOW_LANGUAGES` adds a language menu when `django.conf.urls.i18n` is in your URLs.

Permission values used across the settings (`permission`, `ACTIVITY.view`, `ACTIVITY.others` and so on) accept `"staff"`, `"superuser"`, `"none"`, `"perm:app.codename"`, `"group:Name"`, a list of those, a callable or a dotted path.

### Colours, fonts and corners

`COLORS` takes friendly names and applies them on top of whatever theme is active. Put the same keys under `"dark"` for dark mode only.

| Key | What it changes |
|---|---|
| `accent`, `accent_hover`, `on_accent`, `accent_text` | Buttons, links, focus rings, active items. Setting only `accent` derives the rest |
| `background`, `background_2`, `surface`, `surface_2`, `surface_3` | Page and card backgrounds |
| `border`, `border_strong` | Lines |
| `text`, `text_muted`, `text_subtle` | Text |
| `success`, `warning`, `danger`, `info` | Status colours used by badges, toasts and charts |
| `sidebar`, `sidebar_text`, `sidebar_active`, `sidebar_active_text`, `topbar`, `input`, `heatmap` | Specific parts |
| `chart` | A list of up to six chart colours |

`FONTS` takes `body`, `heading`, `mono` and `size`. Any of the bundled fonts works by name: Geist, Manrope, DM Sans, Figtree, Plus Jakarta Sans, IBM Plex Sans, Nunito, Archivo, Space Grotesk, Source Serif 4, Fraunces, Geist Mono, JetBrains Mono, IBM Plex Mono and Space Mono. For anything else add `"files": ["css/my-font.css"]` (or a Google Fonts URL) and use the family name. `"bundled": False` stops loading the bundled fonts. `FONTS: False` does the same.

`RADIUS` is a length (`"8px"`, `0`) or one of `sharp`, `soft`, `round`.

`TOKENS` is the low level escape hatch. Every CSS variable behind the themes can be set there, so `{"side-w": "280px"}` becomes `--cc-side-w`. Look at the top of `cc_admin/static/cc_admin/css/cc.css` for the full list.

### Appearance panel

Besides theme, mode and density, each user can pick an accent colour, a font, the text size and corner style. It is saved in a cookie, so the page renders right on the first byte. `APPEARANCE` turns each control on or off and sets the choices:

```python
"APPEARANCE": {
    "accent": True,
    "accents": ["#5b5bd6", "#0e8a8a", "#e5484d"],
    "font": True,
    "fonts": ["Geist", "Manrope", "Source Serif 4", "system"],
    "font_size": True,
    "radius": True,
},
```

`APPEARANCE: False` hides all of them. `THEME_SWITCHER: False` hides the whole panel.

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
| `contributions` | The admin log as a GitHub style calendar. `scope` is `me` or `all`, `weeks` sets the length. Days link to the activity page |
| `team` | Who changed the most in the last `days` days. Only shown to users who may see other people's activity |
| `cohort` | `{"headers": [...], "rows": [{"label": ..., "total": ..., "values": [...]}]}`. Cells show the share of `total` |
| `tracker` | A row of coloured bars, like an uptime chart: `[{"label": ..., "summary": ..., "items": [{"tone": "success", "title": ...}]}]` |
| `html` | `template` plus an optional `context` callable, or `html` |

Every widget also takes `title`, `subtitle`, `icon`, `width` (1 to 12), `link`, `link_text` and `permission`. Charts are plain SVG drawn on the server and pick their colours from the theme.

## Activity

`/admin/cc/activity/` shows what everyone did in the admin, built from Django's own `LogEntry` table. Nothing extra is recorded.

- A year long calendar, coloured by how many changes were made each day. Click a day to see exactly what happened: who, which record, and which fields changed.
- Totals, active days, the longest and current streak, the busiest day, and the split between added, changed and deleted.
- A monthly feed, like GitHub's: "Made 368 changes in 4 models", with a bar per model.
- A list of people with their share, the last twelve weeks and the model they touch most. Each person has their own page at `/admin/cc/activity/<id>/`.
- Year tabs, and the same views on the dashboard through the `contributions` and `team` widgets.

```python
"ACTIVITY": {
    "enabled": True,
    "view": "staff",
    "others": "superuser",
    "team": True,
    "details": True,
    "weeks": 53,
    "exclude": ["auth.user"],
    "menu": True,
},
```

`view` decides who can open the activity pages at all. `others` decides who can see other people; everyone else only sees their own page. Use `"staff"` to make the team page open to all staff, `"none"` to keep it private, or `"perm:admin.view_logentry"`, `"group:Managers"` or a callable that gets `(request, user)`. `details: False` hides record names and change messages and keeps only the counts. Record links only show up for models the viewer can open.

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
- `actions_list` and `actions_detail` also take groups, which show up as a dropdown: `{"title": "Reports", "icon": "file-chart-column", "items": ["stock_report", "price_report"]}`.
- `@display` also has `image` (a thumbnail from a URL or an `ImageField`) and `progress` (a bar from a percentage or a `(value, total)` pair).

More options:

| Option | Does |
|---|---|
| `list_sections` | Expandable rows. Each row gets a chevron that opens tables or templates below it |
| `form_sections` | The same sections, shown under the edit form |
| `ordering_field` | Drag and drop rows in the list to reorder them. Saves straight away |
| `list_per_page_options` | Choices for the "Per page" menu. Defaults to `LIST_PER_PAGE_OPTIONS`. The choice is kept per model |
| `list_fullwidth` | Lets the list use the full screen width |
| `list_horizontal_scrollbar_top` | Adds a second horizontal scrollbar above wide tables |
| `list_disable_select_all` | Hides the select all checkbox |
| `change_form_show_cancel_button` | A cancel button in the save bar. Defaults to `FORMS["show_cancel"]` |
| `change_list_before_template`, `change_list_after_template` | Templates included above and below the list |
| `change_form_before_template`, `change_form_after_template` | Templates included above and below the form |

### Sections

```python
from cc_admin.sections import TableSection, TemplateSection


class OrderLines(TableSection):
    verbose_name = "Items"
    related_name = "items"
    fields = ["product", "quantity", "unit_price", "line_total"]
    limit = 10

    def line_total(self, item):
        return item.quantity * item.unit_price


class CustomerMap(TemplateSection):
    template_name = "shop/customer_map.html"


class OrderAdmin(ModelAdmin):
    list_sections = [OrderLines]
    form_sections = [OrderLines]
```

A `TableSection` reads `related_name` from the object, or override `get_queryset()`. Fields can be model fields or methods on the section.

### Widgets

```python
from cc_admin.widgets import CodeWidget, ColorWidget, ImageWidget, JSONWidget, RichTextWidget, SegmentedWidget, SwitchWidget
```

| Widget | Does |
|---|---|
| `SwitchWidget` | A toggle for booleans. `FORMS["switches"] = True` uses it for every `BooleanField` |
| `SegmentedWidget` | Radio choices as one segmented control |
| `ColorWidget` | A hex input with a colour picker |
| `RichTextWidget` | A small editor for HTML text: bold, italic, headings, lists, quotes, links, code. Pasted HTML is cleaned |
| `CodeWidget` | A monospace textarea where Tab indents |
| `JSONWidget` | Pretty prints and checks JSON as you type. Used for every `JSONField` unless `FORMS["json_editor"]` is off |
| `ImageWidget` | A file input that shows the current image and a preview of the new one |
| `CounterTextarea` | A textarea with a character limit |

Text inputs with a `max_length` show a counter while you type. Turn it off with `FORMS["char_counter"] = False`.

### Custom pages

Any view can live inside the admin with the menu, theme and shortcuts:

```python
from cc_admin.views import AdminPageView


class ReportsView(AdminPageView):
    title = "Reports"
    template_name = "shop/reports.html"
    permission_required = "shop.view_order"


class OrderAdmin(ModelAdmin):
    def get_urls(self):
        view = self.admin_site.admin_view(ReportsView.as_view(model_admin=self))
        return [path("reports/", view, name="shop_order_reports")] + super().get_urls()
```

The template extends `cc_admin/page.html` and fills `{% block page %}`.

### Filters

| Filter | Use |
|---|---|
| `FieldTextFilter` | Contains search on one field: `("country", FieldTextFilter)` |
| `FieldExactFilter` | Exact match on one field |
| `TextFilter` | Subclass it, set `parameter_name`, write `queryset()` |
| `RangeNumericFilter` | From and to inputs for numbers |
| `RangeDateFilter` | From and to dates, works on DateField and DateTimeField. Has quick picks for today, 7 days, 30 days, this month and this year |
| `RangeDateTimeFilter` | From and to with time |
| `SliderNumericFilter` | A two handle slider between the lowest and highest value |
| `SingleNumericFilter` | One number, exact match |
| `ChoicesCheckboxFilter` | Pick several choices at once |
| `AllValuesCheckboxFilter` | Pick several of the values that exist in the column |
| `RelatedCheckboxFilter` | Pick several related objects at once |
| `ChoicesDropdownFilter`, `RelatedDropdownFilter`, `AllValuesDropdownFilter`, `DropdownFilter` | A select instead of a long list |
| `BooleanRadioFilter` | Yes, No, All as one segmented control |

Filters live in a side panel. Active filters show as chips above the table, each with its own remove button.

## Keyboard

| Keys | Does |
|---|---|
| `Ctrl K` / `⌘ K` | Command palette: jump to any model, open records found by search, add new records, switch themes |
| `/` | Focus the search box |
| `g d`, `g a`, `g s` | Go to the dashboard, your activity, the site |
| `t` | Appearance panel |
| `[` | Collapse the menu |
| `j` `k` | Move between rows |
| `x`, `Shift X` | Select the row, select all |
| `Enter` `o`, `Shift O` | Open the row, in a new tab |
| `Space` | Expand the row |
| `n` | Add new |
| `f`, `c`, `e` | Filters, columns, export |
| `←` `→` | Previous and next page |
| `Ctrl S` | Save and keep editing |
| `Ctrl Enter` | Save |
| `Ctrl Shift Enter` | Save and add another |
| `Alt ←` `Alt →` | Previous and next form tab |
| `g h`, `g l` | History, back to the list |
| `?` | All shortcuts |

Every key can be changed in settings. Write a combination with `+` and a sequence with a space. `mod` is Ctrl on Windows and Linux and ⌘ on a Mac. Several keys for one action go in a list, and `None` turns an action off.

```python
"SHORTCUTS": {
    "enabled": True,
    "user_editable": True,
    "keys": {
        "filters": "shift+f",
        "open_row": ["o", "enter"],
        "theme": None,
        "delete": "mod+shift+backspace",
    },
    "custom": [
        {"keys": "g o", "title": "Open orders", "link": "admin:shop_order_changelist"},
        {"keys": "g r", "title": "Reports", "link": "admin:shop_order_reports", "permission": "perm:shop.view_order"},
        {"keys": "mod+shift+p", "title": "Print", "click": "#print-button"},
    ],
},
```

The action names are `palette`, `help`, `search`, `dashboard`, `activity`, `site`, `theme`, `menu`, `next_row`, `prev_row`, `select_row`, `select_all`, `open_row`, `open_row_tab`, `expand_row`, `add`, `filters`, `columns`, `export`, `prev_page`, `next_page`, `save`, `save_continue`, `save_add`, `next_tab`, `prev_tab`, `history`, `back` and `delete` (off by default).

With `user_editable` on, people can click any shortcut in the `?` dialog and press new keys. Their choice is kept in their browser and wins over the settings. If the keys were taken by another action, that action loses them. `SHORTCUTS: False` turns the whole thing off.

The command palette takes extra entries too:

```python
"COMMAND_PALETTE": {
    "commands": [{"title": "Weekly reports", "subtitle": "Revenue by channel", "icon": "chart-pie", "link": "admin:shop_order_reports"}],
    "search_callback": "shop.search.palette",
},
```

`search_callback` gets `(request, query)` and returns a list of `{"title", "subtitle", "icon", "link"}` shown above the model results.

## Also in the box

- Column picker on every list, remembered per model.
- A "Per page" menu on every list, remembered per model.
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

Log in with `admin` / `admin`. The example shop uses most of the features above. The seed also adds a small team (`murad`, `leyla`, `elvin`, `nigar`, `sevda`, password same as the name) with a year of admin history, so the activity pages have something to show. Log in as one of them to see what a normal staff user gets. `CC_THEME=terminal python manage.py runserver` starts it in another theme.

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
