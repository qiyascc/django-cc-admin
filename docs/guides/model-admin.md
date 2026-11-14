# ModelAdmin extras

Installing the app already restyles every list and form. To use the extra list and form features, register your models with `cc_admin.admin.ModelAdmin` instead of Django's. It is a subclass of `django.contrib.admin.ModelAdmin`, so everything you already wrote keeps working, and you can switch one model at a time.

```python
from django.contrib import admin

from cc_admin.admin import ModelAdmin

from .models import Order


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["number", "customer", "status", "total"]
```

## Mixing with other admin base classes

If a model admin already inherits from another package's class, such as `ImportExportModelAdmin` or `SimpleHistoryAdmin`, use the mixin and put it first:

```python
from cc_admin.admin import ModelAdminMixin
from import_export.admin import ImportExportModelAdmin


@admin.register(Order)
class OrderAdmin(ModelAdminMixin, ImportExportModelAdmin):
    actions_row = ["refund"]
```

`ModelAdmin` itself is nothing more than `ModelAdminMixin` plus `django.contrib.admin.ModelAdmin`. For inlines there is `InlineMixin`, with ready made `TabularInline` and `StackedInline`.

## Richer list columns with @display

`cc_admin.decorators.display` takes everything Django's `@admin.display` takes (`description`, `ordering`, `boolean`, `empty_value`) and adds a few ways of drawing the value.

```python
from cc_admin.decorators import display


class CustomerAdmin(ModelAdmin):
    list_display = ["person", "email_address", "tier_label", "photo", "profile_done", "tag_list", "api_key"]

    @display(description="Customer", header=True, ordering="name")
    def person(self, obj):
        return obj.name, obj.city

    @display(description="Email", copy=True, ordering="email")
    def email_address(self, obj):
        return obj.email

    @display(description="Tier", label={"standard": "neutral", "silver": "info", "gold": "warning", "vip": "accent"})
    def tier_label(self, obj):
        return obj.tier, obj.get_tier_display()

    @display(description="Photo", image=True)
    def photo(self, obj):
        return obj.avatar

    @display(description="Profile", progress=True)
    def profile_done(self, obj):
        return obj.filled_fields, 12

    @display(description="Tags", tags=True)
    def tag_list(self, obj):
        return [tag.name for tag in obj.tags.all()]

    @display(description="API key", mono=True, copy=True)
    def api_key(self, obj):
        return obj.api_key
```

`header=True`
: A title with a second line under it and a round avatar. Return `title`, `(title, subtitle)` or `(title, subtitle, avatar)`. Without an avatar the initials of the title are used, in a colour picked from the text so the same person always gets the same colour. The avatar may be an image URL, a dict with `image` or `text`, or `False` for none.

`label=...`
: A coloured badge. Return `value` or `(value, text)`. Give a dict that maps values to tones, or one tone for every row, like `label="info"`. The tones are `neutral`, `accent`, `success`, `warning`, `danger` and `info`. Values missing from the dict get `neutral`.

`copy=True`
: The value with a small copy button next to it.

`mono=True`
: The value in the monospace font. Combine it with `copy` for codes and keys.

`tags=True`
: A list of short strings, each drawn as a small badge.

`image=True`
: A thumbnail. Return a URL or an `ImageField` / `FileField` value.

`progress=True`
: A bar. Return a percentage, or `(value, total)`. The bar turns green at 100 percent and red under 15.

An empty value (`None` or an empty string) is drawn as a muted dash by `label` and `image`. With `copy` and `mono` it falls through to Django's normal empty value display.

```{image} ../screenshots/quickstart-list.jpg
:alt: A list with header, badge and row menu columns
```

## List options

| Option | Default | What it does |
| --- | --- | --- |
| `actions_list` | `()` | Buttons next to "Add". See [Actions](actions.md). |
| `actions_row` | `()` | A menu at the end of each row. |
| `actions_detail` | `()` | Buttons at the top of the edit page. |
| `actions_submit_line` | `()` | Extra buttons in the save bar. |
| `list_sections` | `()` | Expandable rows. See [Expandable rows and sections](sections.md). |
| `ordering_field` | `None` | Drag and drop rows to reorder them, saved right away. See below. |
| `list_export` | `None` | `False` turns off export for this model, `True` turns it on. `None` follows the `LIST_EXPORT` setting. See [Export](export.md). |
| `list_per_page_options` | `None` | Choices for the "Per page" menu. `None` uses `LIST_PER_PAGE_OPTIONS`. |
| `list_fullwidth` | `False` | Let the list use the full width of the screen. |
| `list_horizontal_scrollbar_top` | `False` | A second horizontal scrollbar above wide tables, so you do not have to scroll down to scroll sideways. |
| `list_disable_select_all` | `False` | Hide the "select all" checkbox in the header. |
| `change_list_before_template` | `None` | A template included above the list. |
| `change_list_after_template` | `None` | A template included below the list. |

Every list also gets, with no options at all:

- a search box that you can focus with {kbd}`/`,
- a filter side panel ({kbd}`f`) and a chip above the table for each active filter, with its own remove button,
- a column picker ({kbd}`c`), remembered per model in the browser,
- a "Per page" menu, remembered per model in a cookie,
- a floating bar with the bulk actions when rows are selected,
- the date hierarchy as a row of buttons,
- keyboard navigation through the rows.

### Rows per page

```python
CC_ADMIN = {"LIST_PER_PAGE_OPTIONS": [25, 50, 100, 200]}
```

Per model:

```python
class LogAdmin(ModelAdmin):
    list_per_page = 50
    list_per_page_options = [50, 250, 1000]
```

Your `list_per_page` is always added to the choices. A value in the user's cookie that is not one of the choices is ignored.

### Drag and drop sorting

Give the model an integer field for the position and name it in `ordering_field`:

```python
class Category(models.Model):
    name = models.CharField(max_length=80)
    position = models.PositiveIntegerField(default=0)


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name"]
    ordering_field = "position"
    exclude = ["position"]
```

Each row gets a grip handle. Drag a row to a new place and the new order is saved at once, in one transaction, for the rows on the current page. Sorting is only offered to users with change permission, and only while the list is not sorted by a column header. When `ordering` is not set, the list is ordered by `ordering_field` and then by primary key.

## Forms

### Tabs and a side column

Fieldsets with the class `"tab"` become tabs at the top of the form. Fieldsets with the class `"sidebar"` move to a sticky column on the right. Everything else goes into the first tab, called "General".

```python
class ProductAdmin(ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", ("slug", "sku"), "category", "description"]}),
        ("Pricing", {"fields": [("price", "cost"), "has_discount", "discount_percent"], "classes": ["tab"]}),
        ("Inventory", {"fields": [("stock", "launched_on"), "tags"], "classes": ["tab"]}),
        ("Publishing", {"fields": ["status", "is_featured", "created_at"], "classes": ["sidebar"]}),
    ]
```

The tab bar only appears when at least one fieldset or inline is a tab. {kbd}`Alt+→` and {kbd}`Alt+←` move between tabs. Django's own `"collapse"` class still works and draws a fieldset that starts folded.

```{image} ../screenshots/change-form.jpg
:alt: An order form with General and Notes tabs, a Summary side column and extra buttons in the save bar
```

On screens narrower than 1180 pixels the side column moves under the form.

### Inlines

`cc_admin.admin.TabularInline` and `StackedInline` add four options:

```python
from cc_admin.admin import StackedInline, TabularInline


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    ordering_field = "position"
    fields = ["product", "quantity", "unit_price", "position"]


class NoteInline(StackedInline):
    model = Note
    extra = 0
    tab = True
    fields = ["author", "body"]
```

`tab = True`
: The inline gets its own tab, named after the model, with the number of saved rows on it.

`collapsible = True`
: The inline can be folded with a click on its title. It starts open.

`hide_title = True`
: No heading above the inline.

`ordering_field = "position"`
: Rows can be dragged into order. The position field is hidden and filled in when the form is saved. The inline is ordered by that field.

### Fields that depend on other fields

`conditional_fields` hides a field until an expression over the other fields of the form is true:

```python
class OrderAdmin(ModelAdmin):
    conditional_fields = {
        "gift_message": "is_gift",
        "tracking_code": "status in ['shipped', 'delivered']",
        "discount_percent": "has_discount and total > 100",
        "reason": "not (status == 'paid' or status == 'pending')",
    }
```

The check runs in the browser as the user types, so the form changes at once. Expressions know:

- field names of the same form, which give the current value,
- strings in single or double quotes, numbers, `True`, `False` and `None`,
- lists in square brackets,
- `==`, `!=`, `<`, `<=`, `>`, `>=` and `in`,
- `and`, `or`, `not` and parentheses.

A checkbox gives `True` or `False`, a multiple select gives a list of the selected values, and everything else gives a string. When a number is compared with a number, both sides are compared as numbers.

An expression that cannot be read leaves the field visible, so a typo never hides a field for good.

Hidden fields are still submitted. If a hidden value must not be saved, clear it in `save_model` or in the form's `clean()`.

### Other form options

| Option | Default | What it does |
| --- | --- | --- |
| `compressed_fields` | `False` | Labels sit to the left of the inputs instead of above them. Good for long forms. |
| `warn_unsaved_form` | `None` | Ask before leaving a form with unsaved changes. `None` follows `WARN_UNSAVED_FORMS` (default `True`). |
| `change_form_show_cancel_button` | `None` | A "Cancel" button in the save bar. `None` follows `FORMS["show_cancel"]` (default `True`). |
| `change_form_before_template` | `None` | A template included above the form. |
| `change_form_after_template` | `None` | A template included below the form. |
| `form_sections` | `()` | Read only tables or templates under the form. See [sections](sections.md). |

The included templates get the normal admin context, including `original` (the object being edited, on change pages) and `opts`.

### Form defaults for every model

```python
CC_ADMIN = {
    "FORMS": {
        "switches": False,
        "json_editor": True,
        "show_cancel": True,
        "char_counter": True,
    },
    "WARN_UNSAVED_FORMS": True,
}
```

`switches`
: Draw every `BooleanField` as a toggle switch instead of a checkbox.

`json_editor`
: Use the [JSON widget](widgets.md) for every `JSONField`: it pretty prints the value and checks it as you type.

`show_cancel`
: Show a "Cancel" button in the save bar.

`char_counter`
: Text inputs with a `max_length` show a counter while you type.

`switches` and `json_editor` only apply to fields that have no `choices` and no widget of their own, set through `formfield_overrides` or `formfield_for_dbfield`. They work in `cc_admin.admin.ModelAdmin` subclasses.

### The save bar

The save bar sticks to the bottom of the screen. It holds "Delete" on the left, "Cancel" if enabled, your [submit line actions](actions.md#buttons-in-the-save-bar), and Django's save buttons. {kbd}`Ctrl+Enter` saves, {kbd}`Ctrl+S` saves and keeps editing, and {kbd}`Ctrl+Shift+Enter` saves and opens a new form. On a Mac use {kbd}`⌘` instead of {kbd}`Ctrl`.

On the edit page a small card under the side column shows the record number and the model label, and live updates show [who else has the record open](live-updates.md#what-updates).
