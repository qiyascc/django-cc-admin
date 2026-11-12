###############
# Qiyas Sadıqov CC
###############

import contextvars
import csv
import html
import json
import re

from django import forms
from django.contrib import admin
from django.contrib.admin.utils import display_for_field, display_for_value, label_for_field, lookup_field, unquote
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import capfirst
from django.utils.translation import gettext as _

from . import conf
from .icons import icon

TAGS = re.compile(r"<[^>]+>")
_row_actions = contextvars.ContextVar("cc_admin_row_actions", default=None)


class _Echo:
    def write(self, value):
        return value


def plain(value):
    text = TAGS.sub(" ", str(value if value is not None else ""))
    return " ".join(html.unescape(text).split())


class ModelAdminMixin:
    actions_list = ()
    actions_row = ()
    actions_detail = ()
    actions_submit_line = ()
    list_export = None
    compressed_fields = False
    warn_unsaved_form = None
    conditional_fields = {}
    change_form_outer_before = None
    change_form_outer_after = None

    def _cc_action_func(self, name):
        if callable(name):
            return name
        return getattr(self, name, None)

    def _cc_allowed(self, request, func, obj=None):
        for permission in getattr(func, "allowed_permissions", ()):
            checker = getattr(self, f"has_{permission}_permission")
            try:
                ok = checker(request, obj) if permission != "add" else checker(request)
            except TypeError:
                ok = checker(request)
            if not ok:
                return False
        return True

    def _cc_actions(self, request, names, kind, obj=None):
        info = self.opts.app_label, self.opts.model_name
        result = []
        for name in names or ():
            func = self._cc_action_func(name)
            if func is None or not self._cc_allowed(request, func, obj):
                continue
            slug = getattr(func, "cc_url_path", None) or func.__name__.replace("_", "-")
            if kind == "list":
                url = reverse(f"admin:{info[0]}_{info[1]}_cc_action", args=[slug])
            elif kind in ("detail", "row") and obj is not None:
                url = reverse(f"admin:{info[0]}_{info[1]}_cc_object_action", args=[obj.pk, slug])
            else:
                url = ""
            result.append(
                {
                    "name": func.__name__,
                    "slug": slug,
                    "label": getattr(func, "short_description", None) or capfirst(func.__name__.replace("_", " ")),
                    "icon": getattr(func, "cc_icon", None),
                    "variant": getattr(func, "cc_variant", "default"),
                    "confirm": getattr(func, "cc_confirm", None),
                    "attrs": getattr(func, "cc_attrs", {}),
                    "new_tab": getattr(func, "cc_new_tab", False),
                    "url": url,
                }
            )
        return result

    def _cc_find(self, names, slug):
        for name in names or ():
            func = self._cc_action_func(name)
            if func is None:
                continue
            if (getattr(func, "cc_url_path", None) or func.__name__.replace("_", "-")) == slug:
                return func
        return None

    def get_urls(self):
        info = self.opts.app_label, self.opts.model_name
        wrap = self.admin_site.admin_view
        urls = [
            path("cc-export/", wrap(self.cc_export_view), name="%s_%s_cc_export" % info),
            path("cc-action/<slug:slug>/", wrap(self.cc_action_view), name="%s_%s_cc_action" % info),
            path(
                "<path:object_id>/cc-action/<slug:slug>/",
                wrap(self.cc_object_action_view),
                name="%s_%s_cc_object_action" % info,
            ),
        ]
        return urls + super().get_urls()

    def _cc_back(self, request, object_id=None):
        info = self.opts.app_label, self.opts.model_name
        referer = request.META.get("HTTP_REFERER")
        if referer and url_has_allowed_host_and_scheme(
            referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return referer
        if object_id is not None:
            return reverse(f"admin:{info[0]}_{info[1]}_change", args=[object_id])
        return reverse(f"admin:{info[0]}_{info[1]}_changelist")

    def cc_action_view(self, request, slug):
        func = self._cc_find(self.actions_list, slug)
        if func is None or not self._cc_allowed(request, func):
            raise PermissionDenied
        response = func(self, request) if not hasattr(func, "__self__") else func(request)
        return response or HttpResponseRedirect(self._cc_back(request))

    def cc_object_action_view(self, request, object_id, slug):
        obj = self.get_object(request, unquote(object_id))
        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, self.opts, object_id)
        func = self._cc_find(tuple(self.actions_detail) + tuple(self.actions_row), slug)
        if func is None or not self._cc_allowed(request, func, obj):
            raise PermissionDenied
        response = func(self, request, obj) if not hasattr(func, "__self__") else func(request, obj)
        return response or HttpResponseRedirect(self._cc_back(request, object_id))

    def cc_export_enabled(self, request):
        setting = self.list_export if self.list_export is not None else conf.get("LIST_EXPORT")
        return bool(setting) and self.has_view_permission(request)

    def _cc_export_columns(self, request):
        columns = []
        for name in self.get_list_display(request):
            if name in ("action_checkbox", "cc_row_actions"):
                continue
            try:
                label = label_for_field(name, self.model, self)
            except (AttributeError, FieldDoesNotExist):
                continue
            columns.append((name, capfirst(plain(label))))
        return columns

    def _cc_export_value(self, name, obj):
        empty = self.get_empty_value_display()
        try:
            field, attr, value = lookup_field(name, obj, self)
        except (AttributeError, FieldDoesNotExist):
            return ""
        if field is not None:
            return plain(display_for_field(value, field, empty))
        if getattr(attr, "boolean", False):
            return "yes" if value else "no"
        return plain(display_for_value(value, empty))

    def cc_export_rows(self, request, queryset):
        columns = self._cc_export_columns(request)
        yield [label for _, label in columns]
        for obj in queryset.iterator(chunk_size=500):
            yield [self._cc_export_value(name, obj) for name, _ in columns]

    def cc_export_response(self, request, queryset, fmt):
        filename = f"{self.opts.model_name}-export"
        if fmt == "json":
            rows = self.cc_export_rows(request, queryset)
            headers = next(rows)
            data = [dict(zip(headers, row)) for row in rows]
            response = HttpResponse(json.dumps(data, cls=DjangoJSONEncoder, ensure_ascii=False, indent=2), content_type="application/json")
            response["Content-Disposition"] = f'attachment; filename="{filename}.json"'
            return response
        writer = csv.writer(_Echo())
        response = StreamingHttpResponse(
            ("﻿" if i == 0 else "") + writer.writerow(row) for i, row in enumerate(self.cc_export_rows(request, queryset))
        )
        response["Content-Type"] = "text/csv; charset=utf-8"
        response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
        return response

    def cc_export_view(self, request):
        if not self.cc_export_enabled(request):
            raise PermissionDenied
        fmt = request.GET.get("_format", "csv")
        request.GET = request.GET.copy()
        request.GET.pop("_format", None)
        changelist = self.get_changelist_instance(request)
        return self.cc_export_response(request, changelist.get_queryset(request), fmt)

    @admin.action(description="Export selected to CSV")
    def cc_export_csv(self, request, queryset):
        return self.cc_export_response(request, queryset, "csv")

    @admin.action(description="Export selected to JSON")
    def cc_export_json(self, request, queryset):
        return self.cc_export_response(request, queryset, "json")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if self.cc_export_enabled(request) and actions is not None and self.actions is not None:
            for name in ("cc_export_csv", "cc_export_json"):
                func = getattr(type(self), name)
                actions[name] = (func, name, func.short_description)
        return actions

    def get_list_display(self, request):
        display = list(super().get_list_display(request))
        if self.actions_row and "cc_row_actions" not in display:
            display.append("cc_row_actions")
        return display

    @admin.display(description="")
    def cc_row_actions(self, obj):
        request = _row_actions.get()
        if request is None:
            return ""
        actions = self._cc_actions(request, self.actions_row, "row", obj)
        if not actions:
            return ""
        items = format_html_join(
            "",
            '<button type="submit" form="cc-action-form" formaction="{}" class="cc-menu-item cc-tone-{}"{}>{}<span>{}</span></button>',
            (
                (
                    a["url"],
                    a["variant"],
                    format_html(' data-confirm="{}"', a["confirm"]) if a["confirm"] else "",
                    icon(a["icon"]) if a["icon"] else "",
                    a["label"],
                )
                for a in actions
            ),
        )
        return format_html(
            '<div class="cc-row-menu" data-menu><button type="button" class="cc-icon-btn" data-menu-toggle aria-label="{}">{}</button>'
            '<div class="cc-menu" role="menu">{}</div></div>',
            _("Actions"),
            icon("ellipsis"),
            items,
        )

    def changelist_view(self, request, extra_context=None):
        token = _row_actions.set(request)
        try:
            extra = {
                "cc_list_actions": self._cc_actions(request, self.actions_list, "list"),
                "cc_export": self.cc_export_enabled(request),
                "cc_export_url": reverse(f"admin:{self.opts.app_label}_{self.opts.model_name}_cc_export"),
                "cc_model_admin": self,
            }
            extra.update(extra_context or {})
            response = super().changelist_view(request, extra)
            if hasattr(response, "render") and not response.is_rendered:
                response.render()
            return response
        finally:
            _row_actions.reset(token)

    def cc_form_context(self, request, obj=None):
        warn = self.warn_unsaved_form if self.warn_unsaved_form is not None else conf.get("WARN_UNSAVED_FORMS")
        return {
            "cc_detail_actions": self._cc_actions(request, self.actions_detail, "detail", obj) if obj is not None else [],
            "cc_submit_actions": self._cc_actions(request, self.actions_submit_line, "submit", obj),
            "cc_conditional_fields": json.dumps(self.conditional_fields or {}),
            "cc_compressed": self.compressed_fields,
            "cc_warn_unsaved": warn,
            "cc_model_admin": self,
        }

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        obj = None
        if object_id:
            try:
                obj = self.get_object(request, unquote(object_id))
            except Exception:
                obj = None
        extra = self.cc_form_context(request, obj)
        extra.update(extra_context or {})
        return super().changeform_view(request, object_id, form_url, extra)

    def _cc_submit_action(self, request, obj):
        slug = request.POST.get("_cc_action")
        if not slug:
            return None
        func = self._cc_find(self.actions_submit_line, slug)
        if func is None or not self._cc_allowed(request, func, obj):
            raise PermissionDenied
        response = func(self, request, obj) if not hasattr(func, "__self__") else func(request, obj)
        if response is not None:
            return response
        info = self.opts.app_label, self.opts.model_name
        return HttpResponseRedirect(reverse(f"admin:{info[0]}_{info[1]}_change", args=[obj.pk]))

    def response_change(self, request, obj):
        return self._cc_submit_action(request, obj) or super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if request.POST.get("_cc_action") and "_popup" not in request.POST:
            response = super().response_add(request, obj, post_url_continue)
            return self._cc_submit_action(request, obj) or response
        return super().response_add(request, obj, post_url_continue)


class ModelAdmin(ModelAdminMixin, admin.ModelAdmin):
    pass


class InlineMixin:
    collapsible = False
    tab = False
    ordering_field = None
    hide_title = False

    def get_formset(self, request, obj=None, **kwargs):
        if self.ordering_field:
            widgets = dict(kwargs.get("widgets") or {})
            widgets[self.ordering_field] = forms.HiddenInput(attrs={"data-cc-order": "1"})
            kwargs["widgets"] = widgets
        return super().get_formset(request, obj, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if self.ordering_field:
            queryset = queryset.order_by(self.ordering_field)
        return queryset


class TabularInline(InlineMixin, admin.TabularInline):
    pass


class StackedInline(InlineMixin, admin.StackedInline):
    pass


__all__ = ["ModelAdmin", "ModelAdminMixin", "StackedInline", "TabularInline", "InlineMixin"]
