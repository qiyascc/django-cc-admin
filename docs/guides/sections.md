# Expandable rows and sections

A section is a small piece of read only content attached to one object: the lines of an order, the latest orders of a customer, a map, a chart. You can show sections in two places:

- **In the list**, with `list_sections`. Each row gets a chevron on the left. Clicking it, or pressing {kbd}`Space` on the selected row, opens the sections under the row without leaving the list.
- **Under the edit form**, with `form_sections`. The sections appear as cards below the fields and inlines.

```{image} ../screenshots/list-sections.jpg
:alt: An order row opened in the list, showing its items and notes
```

## Table sections

`TableSection` shows related objects as a small table:

```python
from cc_admin.admin import ModelAdmin
from cc_admin.sections import TableSection


class OrderLines(TableSection):
    verbose_name = "Items"
    related_name = "items"
    fields = ["product", "quantity", "unit_price", "line_total"]
    limit = 10

    def line_total(self, item):
        return f"${item.quantity * item.unit_price:,.2f}"

    line_total.short_description = "Line total"


class OrderNotes(TableSection):
    verbose_name = "Notes"
    related_name = "timeline"
    fields = ["author", "body", "created_at"]
    empty_text = "No notes on this order."


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_sections = [OrderLines, OrderNotes]
    form_sections = [OrderLines]
```

| Attribute | Default | Meaning |
| --- | --- | --- |
| `verbose_name` | none | The section title. |
| `related_name` | none | The name of the related manager on the object, such as `items` for `order.items`. |
| `fields` | `()` | The columns. Model fields of the related objects, or methods on the section. With no fields, each row shows `str()` of the object. |
| `limit` | `10` | How many rows to show. Under the table, "And 12 more" tells how many were left out. `None` or `0` shows all. |
| `height` | none | A maximum height in pixels. Taller tables scroll inside the section. |
| `empty_text` | "Nothing here yet." | Shown when there are no rows. |

Columns that are model fields are formatted like the admin formats them: dates in your format, choices with their labels, booleans as icons, foreign keys with `str()`. Column titles come from the field's `verbose_name`, or from `short_description` on a method.

### Your own queryset

Override `get_queryset()` when the rows are not a plain related manager, or when you want a particular order:

```python
class CustomerOrders(TableSection):
    verbose_name = "Latest orders"
    fields = ["number", "status", "total", "created_at"]
    limit = 8

    def get_queryset(self):
        return self.obj.orders.order_by("-created_at")
```

Inside a section, `self.obj` is the object of the row or form, `self.request` the current request and `self.model_admin` the model admin.

## Template sections

`TemplateSection` renders a template of your own:

```python
from cc_admin.sections import TemplateSection


class CustomerMap(TemplateSection):
    verbose_name = "Delivery address"
    template_name = "shop/sections/customer_map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["address"] = self.obj.default_address()
        return context
```

```django
<div class="cc-section">
  <div class="cc-section-head"><b>{{ title }}</b></div>
  <p>{{ address.line1 }}<br>{{ address.city }} {{ address.postcode }}</p>
</div>
```

The context always has `section`, `obj`, `request` and `title`, plus whatever you add.

## Mind the cost

Sections in the list are rendered on the server for every row of the page when the list loads, so opening a row is instant. The price is paid up front: with 100 rows per page and two table sections, that is 200 small queries. Keep it reasonable:

- Keep `limit` small.
- Use `get_queryset()` with `select_related` for the columns you show.
- Use `list_sections` for short, useful summaries and `form_sections` for anything bigger.
- If a list has many rows per page, consider fewer rows per page for that model with `list_per_page`.
