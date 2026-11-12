###############
# Qiyas Sadıqov CC
###############

from django.contrib import admin
from django.contrib.admin.utils import prepare_lookup_value
from django.db import models


class InputFilterMixin:
    is_input = True

    def _take(self, params):
        for p in self.expected_parameters():
            if p not in params:
                continue
            raw = params.pop(p)
            values = [v for v in (raw if isinstance(raw, list) else [raw]) if str(v).strip() != ""]
            if values:
                self.used_parameters[p] = prepare_lookup_value(p, values, getattr(self, "list_separator", ","))

    def value_of(self, name):
        value = self.used_parameters.get(name)
        if isinstance(value, list):
            value = value[-1] if value else ""
            if isinstance(value, list):
                value = ",".join(value)
        return value or ""

    def has_output(self):
        return True

    def get_facet_counts(self, pk_attname, filtered_qs):
        return {}

    def choices(self, changelist):
        return [{"clear": changelist.get_query_string(remove=self.expected_parameters())}]


class FieldTextFilter(InputFilterMixin, admin.FieldListFilter):
    template = "cc_admin/filters/text.html"
    lookup = "icontains"

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.parameter_name = f"{field_path}__{self.lookup}"
        self.field = field
        self.field_path = field_path
        self.title = getattr(field, "verbose_name", field_path)
        admin.ListFilter.__init__(self, request, params, model, model_admin)
        self._take(params)

    def expected_parameters(self):
        return [self.parameter_name]

    def value(self):
        return self.value_of(self.parameter_name)


class FieldExactFilter(FieldTextFilter):
    lookup = "exact"


class TextFilter(InputFilterMixin, admin.SimpleListFilter):
    template = "cc_admin/filters/text.html"

    def __init__(self, request, params, model, model_admin):
        if self.parameter_name is None:
            raise ValueError(f"{type(self).__name__} needs a parameter_name.")
        admin.ListFilter.__init__(self, request, params, model, model_admin)
        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            value = value[-1] if isinstance(value, list) else value
            if str(value).strip():
                self.used_parameters[self.parameter_name] = value
        self.lookup_choices = []

    def lookups(self, request, model_admin):
        return []

    def value(self):
        return self.used_parameters.get(self.parameter_name, "")


class RangeFilterMixin(InputFilterMixin):
    input_type = "number"
    step = "any"
    suffix = ""

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_gte = f"{field_path}{self.suffix}__gte"
        self.lookup_lte = f"{field_path}{self.suffix}__lte"
        self.field = field
        self.field_path = field_path
        self.title = getattr(field, "verbose_name", field_path)
        admin.ListFilter.__init__(self, request, params, model, model_admin)
        self._take(params)

    def expected_parameters(self):
        return [self.lookup_gte, self.lookup_lte]

    def value_from(self):
        return self.value_of(self.lookup_gte)

    def value_to(self):
        return self.value_of(self.lookup_lte)


class RangeNumericFilter(RangeFilterMixin, admin.FieldListFilter):
    template = "cc_admin/filters/range.html"


class SliderNumericFilter(RangeNumericFilter):
    template = "cc_admin/filters/slider.html"
    step = 1

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        bounds = model_admin.get_queryset(request).aggregate(low=models.Min(field_path), high=models.Max(field_path))
        self.low = bounds["low"] if bounds["low"] is not None else 0
        self.high = bounds["high"] if bounds["high"] is not None else 0
        if isinstance(field, (models.DecimalField, models.FloatField)) and self.step == 1:
            self.step = "0.01"
        self.low = int(self.low) if isinstance(self.step, int) else float(self.low)
        self.high = int(-(-self.high // 1)) if isinstance(self.step, int) else float(self.high)


class SingleNumericFilter(InputFilterMixin, admin.FieldListFilter):
    template = "cc_admin/filters/text.html"
    input_type = "number"
    lookup = "exact"

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.parameter_name = f"{field_path}__{self.lookup}" if self.lookup != "exact" else field_path
        self.field = field
        self.field_path = field_path
        self.title = getattr(field, "verbose_name", field_path)
        admin.ListFilter.__init__(self, request, params, model, model_admin)
        self._take(params)

    def expected_parameters(self):
        return [self.parameter_name]

    def value(self):
        return self.value_of(self.parameter_name)


class RangeDateFilter(RangeFilterMixin, admin.FieldListFilter):
    template = "cc_admin/filters/range.html"
    input_type = "date"
    presets = True

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.suffix = "__date" if isinstance(field, models.DateTimeField) else ""
        super().__init__(field, request, params, model, model_admin, field_path)


class RangeDateTimeFilter(RangeFilterMixin, admin.FieldListFilter):
    template = "cc_admin/filters/range.html"
    input_type = "datetime-local"


class DropdownMixin:
    template = "cc_admin/filters/dropdown.html"
    is_dropdown = True


class DropdownFilter(DropdownMixin, admin.SimpleListFilter):
    pass


class ChoicesDropdownFilter(DropdownMixin, admin.ChoicesFieldListFilter):
    pass


class RelatedDropdownFilter(DropdownMixin, admin.RelatedFieldListFilter):
    pass


class AllValuesDropdownFilter(DropdownMixin, admin.AllValuesFieldListFilter):
    pass


class BooleanRadioFilter(admin.BooleanFieldListFilter):
    template = "cc_admin/filters/segmented.html"


class ChoicesCheckboxFilter(InputFilterMixin, admin.FieldListFilter):
    template = "cc_admin/filters/checkbox.html"

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = f"{field_path}__in"
        self.field = field
        self.field_path = field_path
        self.title = getattr(field, "verbose_name", field_path)
        admin.ListFilter.__init__(self, request, params, model, model_admin)
        self._take(params)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def selected(self):
        values = self.used_parameters.get(self.lookup_kwarg, [])
        flat = []
        for v in values:
            flat.extend(v if isinstance(v, list) else [v])
        return {str(v) for v in flat}

    def options(self):
        if self.field.flatchoices:
            return [(str(k), v) for k, v in self.field.flatchoices]
        if self.field.is_relation:
            return [(str(pk), label) for pk, label in self.field.get_choices(include_blank=False)]
        return []

    def choices(self, changelist):
        chosen = self.selected()
        return [
            {"value": value, "display": label, "selected": value in chosen}
            for value, label in self.options()
        ]

    def queryset(self, request, queryset):
        chosen = self.selected()
        if not chosen:
            return queryset
        return queryset.filter(**{self.lookup_kwarg: list(chosen)}).distinct()


class RelatedCheckboxFilter(ChoicesCheckboxFilter):
    pass


class AllValuesCheckboxFilter(ChoicesCheckboxFilter):
    def options(self):
        values = (
            self.model_admin.get_queryset(self.request)
            .exclude(**{f"{self.field_path}__isnull": True})
            .order_by(self.field_path)
            .values_list(self.field_path, flat=True)
            .distinct()
        )
        return [(str(v), str(v)) for v in values[:200]]

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.model_admin = model_admin
        self.request = request
        super().__init__(field, request, params, model, model_admin, field_path)


__all__ = [
    "AllValuesCheckboxFilter",
    "AllValuesDropdownFilter",
    "BooleanRadioFilter",
    "ChoicesCheckboxFilter",
    "ChoicesDropdownFilter",
    "DropdownFilter",
    "FieldExactFilter",
    "FieldTextFilter",
    "RangeDateFilter",
    "RangeDateTimeFilter",
    "RangeNumericFilter",
    "RelatedCheckboxFilter",
    "RelatedDropdownFilter",
    "SingleNumericFilter",
    "SliderNumericFilter",
    "TextFilter",
]
