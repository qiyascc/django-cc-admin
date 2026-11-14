# Export

Every list can be exported to CSV or JSON, either the rows you selected or the whole filtered view. Export is on by default for models registered with `cc_admin.admin.ModelAdmin`.

## Exporting the current view

The "Export" button at the top of the list (or the {kbd}`e` key) offers CSV and JSON. The file contains every row that matches the current search and filters, not only the page you are looking at, in the current sort order.

## Exporting selected rows

Tick some rows and pick "Export selected to CSV" or "Export selected to JSON" from the actions in the selection bar.

## What goes in the file

The columns are the columns of `list_display`, with the same headings as the table:

- model fields are written the way the admin shows them, with choice labels instead of raw values and dates in your date format,
- methods decorated with `@display` give their value with any HTML removed, so a badge becomes its text,
- `boolean=True` columns become `yes` or `no`,
- the checkbox column and the row action menu are left out.

CSV files are UTF-8 with a byte order mark, so Excel opens them with the right characters. The download is streamed, so a list of a hundred thousand rows does not have to fit in memory. JSON files are a list of objects keyed by column heading.

```json
[
  {
    "Product": "Cold brew bottle Kitchen",
    "Price": "44.00",
    "Stock": "80",
    "Status": "Draft"
  }
]
```

The "Product" value above comes from a `header=True` column: the title and subtitle are joined with a space, because the HTML around them is removed. When that matters, add a plain column for export, or override `cc_export_rows` as shown below.

## Turning export off

For the whole site:

```python
CC_ADMIN = {"LIST_EXPORT": False}
```

For one model:

```python
class PaymentAdmin(ModelAdmin):
    list_export = False
```

`list_export = True` turns it on for one model when `LIST_EXPORT` is `False`. Export also needs the view permission on the model.

## Changing what is exported

Override `cc_export_rows`. It receives the request and the queryset, and yields the header row first and then one list per object:

```python
class OrderAdmin(ModelAdmin):
    def cc_export_rows(self, request, queryset):
        yield ["Number", "Customer", "Email", "Total", "Created"]
        for order in queryset.select_related("customer").iterator(chunk_size=500):
            yield [order.number, order.customer.name, order.customer.email, str(order.total), order.created_at.isoformat()]
```

Both CSV and JSON use the same rows. To change the response itself, for example the file name, override `cc_export_response(request, queryset, fmt)`, where `fmt` is `"csv"` or `"json"`.

## The export URL

The export button calls `/admin/<app>/<model>/cc-export/` with the current query string and `_format=csv` or `_format=json`. You can link to it yourself, for example from a dashboard widget, to offer a ready made report:

```text
/admin/shop/order/cc-export/?status__in=refunded&_format=csv
```
