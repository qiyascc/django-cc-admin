###############
# Qiyas Sadıqov CC
###############

from django.contrib.admin.utils import display_for_field, display_for_value, label_for_field, lookup_field
from django.core.exceptions import FieldDoesNotExist
from django.template.loader import render_to_string
from django.utils.text import capfirst


class Section:
    verbose_name = None
    template_name = None
    icon = None

    def __init__(self, model_admin, request, obj):
        self.model_admin = model_admin
        self.request = request
        self.obj = obj

    def get_title(self):
        return self.verbose_name or ""

    def get_context_data(self, **kwargs):
        return {"section": self, "obj": self.obj, "request": self.request, "title": self.get_title(), **kwargs}

    def render(self):
        return render_to_string(self.template_name, self.get_context_data(), request=self.request)


class TableSection(Section):
    template_name = "cc_admin/sections/table.html"
    related_name = None
    fields = ()
    limit = 10
    height = None
    empty_text = None

    def get_queryset(self):
        manager = getattr(self.obj, self.related_name)
        return manager.all()

    def _label(self, model, name):
        method = getattr(self, name, None)
        if callable(method):
            return getattr(method, "short_description", capfirst(name.replace("_", " ")))
        try:
            return capfirst(label_for_field(name, model))
        except (AttributeError, FieldDoesNotExist):
            return capfirst(name.replace("_", " "))

    def _value(self, item, name):
        method = getattr(self, name, None)
        if callable(method):
            return method(item)
        empty = self.model_admin.get_empty_value_display() if self.model_admin else "—"
        try:
            field, attr, value = lookup_field(name, item, None)
        except (AttributeError, FieldDoesNotExist):
            return empty
        if field is not None:
            return display_for_field(value, field, empty)
        return display_for_value(value, empty, boolean=getattr(attr, "boolean", False))

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        total = queryset.count()
        items = list(queryset[: self.limit]) if self.limit else list(queryset)
        model = queryset.model
        fields = list(self.fields) or ["__str__"]
        return super().get_context_data(
            headers=[self._label(model, f) for f in fields],
            rows=[[self._value(item, f) for f in fields] for item in items],
            total=total,
            more=max(0, total - len(items)),
            height=self.height,
            empty_text=self.empty_text,
            **kwargs,
        )


class TemplateSection(Section):
    pass


def render_sections(sections, model_admin, request, obj):
    return [s(model_admin, request, obj).render() for s in sections or ()]
