# Custom pages

Sooner or later an admin needs a page that is not a list or a form: a report, an import screen, a page of settings. `cc_admin.views.AdminPageView` puts any template inside the admin frame, with the menu, the theme, the palette, the shortcuts and the notifications, so it looks and behaves like the rest of the admin.

## A report page

```python
from django.db.models import Count, Sum

from cc_admin.views import AdminPageView

from .models import Order


class ReportsView(AdminPageView):
    title = "Reports"
    subtitle = "Numbers the team asks for every Monday."
    template_name = "shop/reports.html"
    permission_required = "shop.view_order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rows"] = Order.objects.values("channel").annotate(n=Count("id"), revenue=Sum("total")).order_by("-revenue")
        return context
```

The template extends `cc_admin/page.html` and fills the `page` block:

```django
{% extends "cc_admin/page.html" %}
{% load cc_admin %}

{% block page %}
<div class="cc-grid">
  <section class="cc-card cc-span-8">
    <header class="cc-card-head">
      <div>
        <span class="cc-card-icon">{% icon "chart-pie" %}</span>
        <div><h2>Revenue by channel</h2><p>All orders, all time</p></div>
      </div>
    </header>
    <table class="cc-table">
      <thead><tr><th>Channel</th><th>Orders</th><th>Revenue</th></tr></thead>
      <tbody>
        {% for row in rows %}
          <tr><td>{{ row.channel|capfirst }}</td><td>{{ row.n }}</td><td>${{ row.revenue|floatformat:2 }}</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </section>
  <section class="cc-card cc-span-4">
    <header class="cc-card-head"><div><span class="cc-card-icon">{% icon "info" %}</span><div><h2>About this page</h2></div></div></header>
    <p class="cc-muted">A plain Django view inside the admin frame.</p>
  </section>
</div>
{% endblock %}
```

`cc_admin/page.html` draws the breadcrumbs, the title and the subtitle for you.

## Wiring it up

### Under a model

The page belongs to a model when it is about that model's data. Add it in `get_urls()` of the model admin, and wrap it in `admin_view()` so only signed in staff can open it:

```python
from django.urls import path


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    def get_urls(self):
        view = self.admin_site.admin_view(ReportsView.as_view(model_admin=self))
        return [path("reports/", view, name="shop_order_reports")] + super().get_urls()
```

The page is now at `/admin/shop/order/reports/`, its URL name is `admin:shop_order_reports`, and the breadcrumbs show the app it belongs to.

### On its own

For a page that belongs to no model, add it to your URLs in front of the admin:

```python
from django.contrib import admin
from django.urls import path

from shop.views import SettingsView

urlpatterns = [
    path("admin/settings/", admin.site.admin_view(SettingsView.as_view()), name="admin_settings"),
    path("admin/", admin.site.urls),
]
```

Give `admin_site=` to `as_view()` if the page belongs to a custom `AdminSite`. Without it, `admin.site` is used.

### In the menu, the palette and the keyboard

A custom page is not listed anywhere until you add it:

```python
CC_ADMIN = {
    "SIDEBAR": {
        "navigation": [
            {"title": "Store", "items": [
                {"title": "Reports", "icon": "chart-pie", "link": "admin:shop_order_reports"},
            ]},
        ],
    },
    "COMMAND_PALETTE": {
        "commands": [{"title": "Weekly reports", "subtitle": "Revenue by channel", "icon": "chart-pie", "link": "admin:shop_order_reports"}],
    },
    "SHORTCUTS": {
        "custom": [{"keys": "g r", "title": "Reports", "link": "admin:shop_order_reports"}],
    },
    "TABS": [
        {"pages": ["admin:shop_order_reports"], "models": ["shop.order"], "items": [
            {"title": "Orders", "link": "admin:shop_order_changelist"},
            {"title": "Reports", "link": "admin:shop_order_reports"},
        ]},
    ],
}
```

## AdminPageView options

| Attribute | Default | Meaning |
| --- | --- | --- |
| `title` | `""` | The page heading and the end of the breadcrumbs. |
| `subtitle` | `""` | A line under the heading. |
| `icon` | `None` | Available to your template as `cc_page.icon`. |
| `template_name` | `"cc_admin/page.html"` | Your template. |
| `permission_required` | `()` | A permission string such as `"shop.view_order"`, a tuple of them (all are needed), or a callable that takes the request. Users without it get a 403. |
| `model_admin` | `None` | The model admin the page belongs to. Sets the breadcrumbs and `opts`. |
| `admin_site` | `None` | The admin site, when there is no model admin. Defaults to `admin.site`. |

`AdminPageView` is a `TemplateView`, so `get_context_data()`, `post()` and the other usual methods work. The context has everything an admin page has (`site_header`, `available_apps`, `user` and so on), plus `title`, `subtitle`, `opts` when there is a model admin, and `cc_page`, the view itself.

## Building blocks for templates

The CSS of the admin is available to your pages:

| Class | Use |
| --- | --- |
| `cc-grid` | A twelve column grid, the same as the dashboard. |
| `cc-span-1` to `cc-span-12` | How many columns a child of `cc-grid` takes. |
| `cc-card` | A card with the theme's surface, border and radius. |
| `cc-card-head` | The header of a card, with `cc-card-icon`, an `h2` and a `p`. |
| `cc-table` | A table styled like the lists. |
| `cc-btn`, `cc-btn-primary`, `cc-btn-danger` | Buttons. |
| `cc-badge cc-tone-success` | A badge. The tones are `neutral`, `accent`, `success`, `warning`, `danger` and `info`. |
| `cc-note cc-tone-warning` | A coloured note box. |
| `cc-muted` | Muted text. |

And the template tags from `{% load cc_admin %}`, such as `{% icon %}` and the `cc_compact` filter that turns 73386 into `73.4k`. See [Templates](../reference/templates.md).

## A page with a form

```python
from django import forms
from django.contrib import messages
from django.shortcuts import redirect


class PriceChangeForm(forms.Form):
    percent = forms.DecimalField(max_digits=5, decimal_places=2, help_text="Use a negative number to lower prices.")


class PriceChangeView(AdminPageView):
    title = "Change all prices"
    template_name = "shop/price_change.html"
    permission_required = "shop.change_product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", PriceChangeForm())
        return context

    def post(self, request, *args, **kwargs):
        form = PriceChangeForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))
        changed = apply_price_change(form.cleaned_data["percent"])
        messages.success(request, f"{changed} prices updated.")
        return redirect("admin:shop_product_changelist")
```

```django
{% extends "cc_admin/page.html" %}

{% block page %}
<form method="post" class="cc-card">
  {% csrf_token %}
  {{ form.as_div }}
  <button type="submit" class="cc-btn cc-btn-primary">Apply</button>
</form>
{% endblock %}
```

`apply_price_change` stands for your own code.
