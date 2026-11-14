# Filters

On every list, filters move out of the right hand column and into a side panel that opens with the "Filters" button or the {kbd}`f` key. Active filters show up as chips above the table, each with its own remove button, so you can see at a glance why a list is shorter than you expected. Django's own filters keep working in the panel.

```{image} ../screenshots/filters.jpg
:alt: The filter panel with checkboxes, a slider and a date range with presets
```

`cc_admin.filters` adds filters that the stock admin lacks: free text, ranges, sliders, several values at once, dropdowns and a segmented yes or no. Use them like any Django filter, as a `(field, FilterClass)` pair in `list_filter`:

```python
from cc_admin.admin import ModelAdmin
from cc_admin.filters import (
    AllValuesCheckboxFilter,
    BooleanRadioFilter,
    ChoicesCheckboxFilter,
    FieldTextFilter,
    RangeDateFilter,
    RelatedDropdownFilter,
    SliderNumericFilter,
)


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_filter = [
        ("status", ChoicesCheckboxFilter),
        ("channel", AllValuesCheckboxFilter),
        ("customer", RelatedDropdownFilter),
        ("total", SliderNumericFilter),
        ("created_at", RangeDateFilter),
        ("tracking_code", FieldTextFilter),
        ("is_gift", BooleanRadioFilter),
    ]
```

The filters work with Django's `ModelAdmin` too, but the side panel and the chips come with any model admin once the app is installed.

## Text filters

`FieldTextFilter`
: A text box that keeps rows whose field contains the text, ignoring case (`icontains`). `("country", FieldTextFilter)`

`FieldExactFilter`
: The same box, but the value must match exactly (`exact`).

`TextFilter`
: A text box with your own logic. Subclass it, set `title` and `parameter_name`, and write `queryset()`:

```python
from django.db.models import Q

from cc_admin.filters import TextFilter


class CustomerSearchFilter(TextFilter):
    title = "Customer name or email"
    parameter_name = "customer"

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(Q(customer__name__icontains=value) | Q(customer__email__icontains=value))


class OrderAdmin(ModelAdmin):
    list_filter = [CustomerSearchFilter]
```

A `TextFilter` without `parameter_name` raises a `ValueError` as soon as the list is opened, so a forgotten line shows up at once.

To match a different lookup with the field filters, subclass and change `lookup`:

```python
class StartsWithFilter(FieldTextFilter):
    lookup = "istartswith"
```

## Range filters

`RangeNumericFilter`
: Two number inputs, "From" and "To". Either side may be left empty.

`SliderNumericFilter`
: A slider with two handles between the lowest and highest value in the column. Decimal and float fields step by 0.01, integers by 1.

`SingleNumericFilter`
: One number input, exact match.

`RangeDateFilter`
: Two date inputs. It works on `DateField` and on `DateTimeField` (comparing the date part). It also offers quick picks: Today, Yesterday, 7 days, 30 days, This month and This year.

`RangeDateTimeFilter`
: Two inputs with date and time.

The range filters produce ordinary query parameters such as `total__gte=100&total__lte=500` or `created_at__date__gte=2026-11-01`, so you can link to a filtered list from anywhere, for example from a [tab](navigation.md#tabs-above-a-list) or a dashboard widget.

## Picking several values

`ChoicesCheckboxFilter`
: A checkbox for every choice of a field with `choices`, or for every object of a foreign key. Rows match any of the ticked values.

`RelatedCheckboxFilter`
: The same for relations. It exists so `list_filter` reads well: `("category", RelatedCheckboxFilter)`.

`AllValuesCheckboxFilter`
: A checkbox for each distinct value that exists in the column, up to 200 values. Useful for plain text columns with a small set of values, like a channel or a country code.

The checkbox filters use the `__in` lookup, so a link such as `/admin/shop/order/?status__in=pending,paid` opens the list with two statuses ticked.

## Dropdowns

When a filter would list dozens of options, a dropdown is easier to use:

`ChoicesDropdownFilter`
: Django's choices filter as a select.

`RelatedDropdownFilter`
: Django's related filter as a select. Good for foreign keys with many rows.

`AllValuesDropdownFilter`
: Django's all values filter as a select.

`DropdownFilter`
: A `SimpleListFilter` that is drawn as a select. Subclass it exactly like `SimpleListFilter`, with `lookups()` and `queryset()`:

```python
from cc_admin.filters import DropdownFilter


class PriceBandFilter(DropdownFilter):
    title = "price band"
    parameter_name = "band"

    def lookups(self, request, model_admin):
        return [("cheap", "Under $20"), ("mid", "$20 to $100"), ("premium", "Over $100")]

    def queryset(self, request, queryset):
        if self.value() == "cheap":
            return queryset.filter(price__lt=20)
        if self.value() == "mid":
            return queryset.filter(price__gte=20, price__lte=100)
        if self.value() == "premium":
            return queryset.filter(price__gt=100)
        return queryset
```

## Yes or no

`BooleanRadioFilter`
: Django's boolean filter as one segmented control: All, Yes, No.

## Using the panel

- {kbd}`f` opens and closes the panel.
- Each filter is a section that can be folded.
- Changes in text, range and checkbox filters are applied with the "Apply" button at the bottom, so you can set several at once.
- The "Show counts" link turns on Django's facet counts, the number of rows behind each option.
- Each active filter appears as a chip above the table. The "×" on a chip removes just that filter.
