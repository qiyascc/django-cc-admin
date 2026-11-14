# Templates

django-cc-admin replaces Django's admin templates with its own, under the same names, so your overrides of `admin/base_site.html`, `admin/change_form.html` and friends keep working the way Django documents them. This page lists the blocks you can override, the templates of the package's own parts, and the template tags you can use in your templates.

## Overriding templates

Put your template in a folder listed in `TEMPLATES["DIRS"]`, which Django searches before app folders:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [...]},
    },
]
```

```text
templates/
└── admin/
    └── base_site.html
```

Extend the package's template rather than copying it, so you keep getting its updates:

```django
{% extends "admin/base.html" %}

{% block extrahead %}
  {{ block.super }}
  <script defer data-domain="admin.example.com" src="https://plausible.io/js/script.js"></script>
{% endblock %}

{% block footer %}Northwind Ltd · Internal use only{% endblock %}
```

For CSS and JavaScript alone, the `STYLES` and `SCRIPTS` settings are simpler than a template override.

## Blocks in admin/base.html

| Block | Holds |
| --- | --- |
| `title` | The browser tab title. |
| `extrastyle` | Extra `<link>` and `<style>` tags in the head. |
| `extrahead` | Anything else in the head. |
| `bodyclass` | Classes on `<body>`. |
| `breadcrumbs` | The breadcrumbs in the top bar. |
| `nav-global` | Space in the top bar, before the search box. |
| `usertools` | The user menu. |
| `messages` | Django messages, shown as toasts. |
| `pretitle` | Above the page title. |
| `content_title` | The page title. |
| `content_subtitle` | The subtitle. |
| `object-tools` | The buttons to the right of the title. |
| `content` | The page content. |
| `sidebar` | Django's right hand sidebar on the index page (unused by the dashboard). |
| `footer` | The page footer. |
| `extrabody` | The end of `<body>`. |
| `cc_tabs` | The row of [tabs](../guides/navigation.md#tabs-above-a-list) above the content. |

The list, form, delete, history and login templates keep Django's block names, such as `field_sets`, `inline_field_sets`, `submit_buttons_bottom`, `result_list`, `search` and `filters`.

## Templates of the package's own parts

These live under `cc_admin/` and can be overridden the same way:

| Template | Draws |
| --- | --- |
| `cc_admin/page.html` | The base for [custom pages](../guides/custom-pages.md). Fill `{% block page %}`. |
| `cc_admin/widgets/<type>.html` | One dashboard widget type, such as `kpi.html` or `chart.html`. |
| `cc_admin/widgets/_head.html` | The header of a widget card. |
| `cc_admin/sections/table.html` | A `TableSection`. |
| `cc_admin/filters/text.html`, `range.html`, `slider.html`, `checkbox.html`, `dropdown.html`, `segmented.html` | The filters in `cc_admin.filters`. |
| `cc_admin/activity/team.html`, `user.html`, `calendar.html`, `feed.html` | The activity pages. |
| `cc_admin/notifications/list.html`, `send.html` | The notification pages. |
| `cc_admin/sidebar.html`, `usermenu.html`, `bell.html`, `tabs.html` | Parts of the frame. |
| `cc_admin/announcements.html` | Banners and modal announcements. |
| `cc_admin/overlays.html` | The palette, the appearance panel, the shortcut dialog and the notification settings. |

Widget templates receive `widget`, a dict with `type`, `spec` (your widget settings), `data` (what the builder made from your data), `width` and `url`.

## Template tags and filters

Load them with `{% load cc_admin %}`.

`{% icon name [class] [label] %}`
: A bundled Lucide icon as inline SVG. Unknown names draw a dot.

  ```django
  {% icon "package" %}
  {% icon "triangle-exclamation-point" "big-icon" "Warning" %}
  ```

`value|cc_compact` and `value|cc_compact:"$"`
: Shortens numbers: `73386` becomes `73.4k`, `2400000` becomes `2.4M`. The argument is a prefix.

`value|cc_initials`
: The first letters of the first two words, upper case: `"Leyla Aliyeva"` becomes `LA`.

`{% cc_spark values [height] %}`
: A small SVG line chart from a list of numbers, like the KPI sparklines. Height defaults to 40 pixels.

`{% cc_nonce %}`
: Outputs ` nonce="..."` when your project sets a CSP nonce, for inline `<script>` and `<style>` tags.

  ```django
  <script{% cc_nonce %}>console.log("ready")</script>
  ```

`value|cc_json`
: The value as JSON, safe to put in an HTML attribute or a script.

`value|cc_split:","`
: Splits a string into a list and drops empty parts.

`mapping|cc_get:key`
: Looks up a key in a dict, which Django templates cannot do with a variable key.

The other tags in the library (`cc_setup`, `cc_tokens`, `cc_dashboard`, `cc_row_meta` and so on) are used by the package's own templates and may change between versions.

## The cc context

Every admin page has a `cc` variable with the resolved settings, made by `{% cc_setup %}` in `admin/base.html`. Useful parts:

| Name | Holds |
| --- | --- |
| `cc.header`, `cc.subheader`, `cc.title` | The site name, subheader and title. |
| `cc.theme` | The active theme: `cc.theme.key`, `cc.theme.label`, `cc.theme.layout`. |
| `cc.scheme`, `cc.density`, `cc.layout` | The resolved mode, density and layout. |
| `cc.environment` | `{"label", "tone"}` or `None`. |
| `cc.version` | The installed version of django-cc-admin. |

## CSS hooks

The `<html>` element has the class `cc` and the attributes `data-skin` (theme key), `data-theme` (the built in theme behind it), `data-scheme`, `data-layout` and `data-density`. `<body>` keeps Django's usual classes, such as `change-list`, `change-form`, `app-shop` and `model-order`, so you can target one model's pages:

```css
html.cc body.model-order .cc-card {
  border-color: var(--cc-accent);
}
```

All theme values are CSS custom properties named `--cc-*`, listed at the top of `cc_admin/static/cc_admin/css/cc.css`.
