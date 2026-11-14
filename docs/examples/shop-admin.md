# Recipe: a shop admin

The repository has an example project, a furniture shop called Northwind, that uses almost every feature of the package. This recipe gets it running and then walks through how each model admin is put together, so you can lift the parts you need.

## Run it

```bash
git clone https://github.com/qiyascc/django-cc-admin
cd django-cc-admin
python3 -m venv .venv
source .venv/bin/activate
pip install django
cd example
python manage.py migrate
python manage.py seed
python manage.py runserver
```

`manage.py` adds the repository folder to the Python path, so the example uses the code from your checkout without installing the package. `seed` makes 35 products, 320 customers and 2200 orders spread over the last year. Pass `--orders 500` for a smaller shop.

Sign in at `http://127.0.0.1:8000/admin/` as `admin` with the password `admin`.

The seed also adds a small team with a year of admin history, so the activity pages have something to show: `murad`, `leyla`, `elvin`, `nigar` and `sevda`, each with the password equal to the username. Sign in as one of them to see what a staff user without superuser rights gets.

Some environment variables change how it runs:

| Variable | Effect |
| --- | --- |
| `CC_THEME=terminal` | Start in another theme. |
| `CC_LIVE=sse` | Use Server-Sent Events instead of polling. |
| `CC_VAPID_PUBLIC`, `CC_VAPID_PRIVATE` | Turn Web Push on with these keys. |
| `DATABASE_PATH=/tmp/shop.sqlite3` | Keep the database somewhere else. |

To watch live updates, run this in a second terminal while the admin is open:

```bash
python manage.py simulate
```

It places a fake order every 8 seconds (`--every 3` for faster, `--count 10` to stop after ten). New rows appear in the order list, the badge next to "Orders" goes up, the dashboard changes and a "New order" popup plays the `cash` sound.

## The models

`example/shop/models.py` has seven models: `Category`, `Tag`, `Product`, `Customer`, `Order`, `OrderItem` and `Note`. Orders have a status (`pending`, `paid`, `shipped`, `delivered`, `refunded`, `cancelled`) and a sales channel. Categories and order items have a `position` field for drag and drop sorting.

## Categories: sorting and expandable rows

```python
class CategoryProducts(TableSection):
    verbose_name = "Products"
    related_name = "products"
    fields = ["name", "sku", "price", "stock"]
    limit = 6


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name", "swatch", "slug", "product_count"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]
    ordering_field = "position"
    list_sections = [CategoryProducts]
    exclude = ["position", "color"]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "hex_color":
            kwargs["widget"] = ColorWidget
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @display(description="Colour")
    def swatch(self, obj):
        return format_html('<span class="cc-badge" style="--tone:{}">{}</span>', obj.hex_color, obj.hex_color)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(n=Count("products"))

    @display(description="Products", ordering="n")
    def product_count(self, obj):
        return obj.n
```

- `ordering_field = "position"` lets you drag categories into order. The field itself is excluded from the form.
- `list_sections` opens the first six products of a category under its row.
- `ColorWidget` gives the colour field a picker.
- The swatch column shows a badge in the category's own colour by setting the `--tone` variable inline.

## Products: filters, actions, tabs and conditions

```python
@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ["product", "sku", "category", "price", "stock_level", "status_label", "is_featured"]
    list_filter = [
        ("status", ChoicesCheckboxFilter),
        ("category", RelatedDropdownFilter),
        ("price", SliderNumericFilter),
        "is_featured",
        ("launched_on", RangeDateFilter),
    ]
    search_fields = ["name", "sku"]
    autocomplete_fields = ["category"]
    filter_horizontal = ["tags"]
    actions_list = ["sync_inventory", {"title": "Reports", "icon": "file-chart-column", "items": ["stock_report", "price_report"]}]
    actions_row = ["duplicate", "archive"]
    actions_detail = ["preview"]
    conditional_fields = {"discount_percent": "has_discount"}
    fieldsets = [
        (None, {"fields": ["name", ("slug", "sku"), "category", "description"]}),
        ("Pricing", {"fields": [("price", "cost"), "has_discount", "discount_percent"], "classes": ["tab"]}),
        ("Inventory", {"fields": [("stock", "launched_on"), "tags", "specs"], "classes": ["tab"]}),
        ("Publishing", {"fields": ["status", "is_featured", "created_at"], "classes": ["sidebar"]}),
    ]

    @display(description="Product", header=True, ordering="name")
    def product(self, obj):
        return obj.name, obj.category.name

    @display(description="Stock", ordering="stock", progress=True)
    def stock_level(self, obj):
        return obj.stock, 240
```

Things to look at:

- The stock column is a progress bar against a target of 240.
- Five filters of four kinds, plus Django's own boolean filter for `is_featured`.
- A "Sync inventory" button and a "Reports" dropdown next to "Add product", a "⋯" menu with "Duplicate" and "Archive" on each row, and a "Preview" button on the edit page. "Archive" asks for confirmation first.
- The form has a "General" tab, "Pricing" and "Inventory" tabs, and a "Publishing" column on the right. "Discount percent" only appears when "Has discount" is ticked.
- `specs` is a `JSONField`, so it gets the JSON editor. The description uses `RichTextWidget` and the status uses `SegmentedWidget`, both set in `formfield_for_dbfield`.

## Customers: header columns, copy buttons, compact forms

```python
@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ["person", "email_address", "country", "tier_label", "orders_count", "is_active", "joined_at"]
    list_filter = ["tier", "is_active", ("country", FieldTextFilter), ("joined_at", RangeDateFilter)]
    compressed_fields = True
    actions_row = ["send_reset"]
    form_sections = [CustomerOrders]

    @display(description="Email", copy=True, ordering="email")
    def email_address(self, obj):
        return obj.email
```

- Each email has a copy button.
- `compressed_fields` puts labels next to the inputs, which suits a long customer form.
- `form_sections` shows the customer's latest eight orders under the form, using a `TableSection` with its own `get_queryset()`.
- The notes fieldset uses Django's `"collapse"` class and starts folded.

## Orders: inlines, sections, submit actions and a custom page

```python
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["number", "customer_link", "status_label", "channel", "items_count", "total", "created_at"]
    list_filter = [("status", ChoicesCheckboxFilter), ("channel", AllValuesCheckboxFilter), ("total", SliderNumericFilter), ("created_at", RangeDateFilter), "is_gift"]
    inlines = [OrderItemInline, NoteInline]
    list_sections = [OrderLines, OrderNotes]
    list_horizontal_scrollbar_top = True
    actions = ["mark_shipped"]
    actions_detail = ["print_invoice"]
    actions_submit_line = ["save_and_notify"]
    conditional_fields = {
        "gift_message": "is_gift",
        "tracking_code": "status in ['shipped', 'delivered']",
        "shipped_at": "status in ['shipped', 'delivered']",
    }

    def get_urls(self):
        view = self.admin_site.admin_view(ReportsView.as_view(model_admin=self))
        return [path("reports/", view, name="shop_order_reports")] + super().get_urls()
```

- `OrderItemInline` is a tabular inline with `ordering_field = "position"`, so order lines can be dragged.
- `NoteInline` is a stacked inline with `tab = True`, so notes get their own tab with a count.
- Each row opens to show the order lines and notes.
- The save bar has "Save and email customer" next to Django's buttons.
- Tracking code and ship date only show up once the status is shipped or delivered.
- `ReportsView` is a [custom page](../guides/custom-pages.md) at `/admin/shop/order/reports/`, linked from the sidebar, the palette and the {kbd}`g` {kbd}`r` shortcut.

## The settings

`example/project/settings.py` holds the `CC_ADMIN` setting that ties it together: a Northwind theme built on Aurora, a sidebar group with live badges for pending orders and low stock, tabs for order statuses, a dashboard with every widget type, notification rules for new orders, refunds and low stock, two announcements, custom shortcuts and palette commands, and an environment badge that says "Staging". It is a good file to copy from.

## Next

- The dashboard of this project is explained piece by piece in [A live order dashboard](live-dashboard.md).
- The notification rules are explained in [Telling staff about changes](notify-from-code.md).
