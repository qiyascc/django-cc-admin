# Branding and the site frame

This page covers everything around the content: the name and logo in the corner, the browser tab title, the environment badge, the sign in page, the user menu, the footer and the small buttons on edit pages.

## Name and title

```python
CC_ADMIN = {
    "SITE_HEADER": "Northwind",
    "SITE_SUBHEADER": "Store admin",
    "SITE_TITLE": "Northwind admin",
    "SITE_URL": "/",
}
```

`SITE_HEADER`
: The name in the top left corner and on the sign in page. Falls back to `admin.site.site_header`, so if you already set that on your `AdminSite`, you do not need this.

`SITE_SUBHEADER`
: A smaller line under the name.

`SITE_TITLE`
: The end of the browser tab title. Falls back to `admin.site.site_title`.

`SITE_URL`
: Where "View site" and the {kbd}`g` {kbd}`s` shortcut go. Falls back to `admin.site.site_url`. Setting it to `None` is the same as leaving it out. To hide the link, set `site_url = None` on your `AdminSite`, as you would with the stock admin.

All four accept a callable that takes the request, which is useful when one code base serves several brands:

```python
def header(request):
    return "Northwind EU" if request.get_host().endswith(".eu") else "Northwind"


CC_ADMIN = {"SITE_HEADER": header}
```

## Logo, icon and favicon

Without a logo the corner shows a square with the initials of `SITE_HEADER`. You have three ways to change that.

**A Lucide icon in the square.** The quickest option. Any of the bundled Lucide names works:

```python
CC_ADMIN = {"SITE_SYMBOL": "store"}
```

**Your own small icon in the square**, next to the name:

```python
CC_ADMIN = {"SITE_ICON": "img/icon.svg"}
```

**A full logo** that replaces the square and the name:

```python
CC_ADMIN = {
    "SITE_LOGO": {"light": "img/logo-dark.svg", "dark": "img/logo-light.svg"},
}
```

`SITE_LOGO` and `SITE_ICON` take one path, or a dict with a `light` and a `dark` version. The light version is shown on light themes, so it is usually the dark coloured file. If you give only one of the two, it is used for both modes.

The favicon is separate:

```python
CC_ADMIN = {"SITE_FAVICON": "img/favicon.png"}
```

Every image setting takes a static path (resolved with `{% static %}`), an absolute path starting with `/`, a full URL, or a `data:` URL.

## A menu for switching sites

If you run several admins, `SITE_DROPDOWN` adds a small menu next to the brand:

```python
CC_ADMIN = {
    "SITE_DROPDOWN": [
        {"title": "Northwind store", "icon": "store", "link": "/"},
        {"title": "Warehouse admin", "icon": "warehouse", "link": "https://warehouse.example.com/admin/", "new_tab": True},
        {"title": "Status page", "icon": "activity", "link": "https://status.example.com/", "permission": "superuser"},
    ],
}
```

Each item takes `title`, `icon`, `link`, an optional `new_tab` and an optional `permission`. The list itself and each item may also be a callable that takes the request.

## Environment badge

A coloured badge in the top bar makes it obvious which copy of the admin you are in:

```python
CC_ADMIN = {
    "ENVIRONMENT": ("Staging", "warning"),
    "ENVIRONMENT_TITLE_PREFIX": True,
}
```

`ENVIRONMENT` takes:

- a string, shown with the `warning` tone,
- a tuple of `(label, tone)`,
- a dict with `label` and `tone`,
- a callable or a dotted path that returns any of the above, or `None` to show nothing.

The tones are `neutral`, `accent`, `success`, `warning`, `danger` and `info`.

With `ENVIRONMENT_TITLE_PREFIX: True`, every browser tab title starts with the label in brackets, like `[Staging] Orders`. You can also give a string, which is used as it is.

A typical setup reads the environment from the server:

```python
import os

ENV = os.environ.get("APP_ENV", "production")

CC_ADMIN = {
    "ENVIRONMENT": None if ENV == "production" else (ENV.title(), "danger" if ENV == "staging" else "info"),
    "ENVIRONMENT_TITLE_PREFIX": True,
}
```

## The sign in page

The sign in page is split in two: a picture side with the brand and a short text, and a card with the form.

```python
CC_ADMIN = {
    "LOGIN": {
        "title": "Run the whole store from one place.",
        "text": "Orders, stock and customers, with the numbers that matter on the first screen.",
        "image": "img/login.jpg",
    },
}
```

`title`
: The large text on the picture side. Defaults to `SITE_HEADER`.

`text`
: A paragraph under it.

`image`
: A background picture for that side. Without one, the theme draws its own background.

`title` and `text` can be callables that take the request.

## User menu links

The menu under your name in the top right corner holds "My activity", "View site", the theme switcher, the keyboard shortcuts, "Change password" and "Log out". If `django.contrib.admindocs` is installed, a "Documentation" link appears too. Your own links go right after "View site":

```python
CC_ADMIN = {
    "USER_LINKS": [
        {"title": "Store front", "icon": "store", "link": "/"},
        {"title": "Help centre", "icon": "life-buoy", "link": "https://help.example.com/"},
        {"title": "Billing", "icon": "credit-card", "link": "admin:billing_invoice_changelist", "permission": "perm:billing.view_invoice"},
    ],
}
```

Each link takes `title`, `icon`, `link` and an optional `permission`. As with `SITE_DROPDOWN`, the list and each item may be callables.

## Language menu

If your project is translated, `SHOW_LANGUAGES` adds a menu for switching language:

```python
CC_ADMIN = {"SHOW_LANGUAGES": True}
```

It lists every entry of `settings.LANGUAGES` in its own language and posts to Django's `set_language` view, so you need `django.conf.urls.i18n` in your URLs:

```python
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
]
```

If the `set_language` URL cannot be found, the menu stays hidden.

## Footer

The stock admin has no footer. You can add one:

```python
CC_ADMIN = {"FOOTER": "Northwind Ltd · Internal use only"}
```

The value is escaped. For links or other HTML, return a safe string from a callable:

```python
from django.utils.html import format_html


def footer(request):
    return format_html('Need help? <a href="{}">Ask in #admin</a>', "https://chat.example.com/admin")


CC_ADMIN = {"FOOTER": footer}
```

You can also override the `footer` block in your own `admin/base_site.html`.

## Buttons on the edit page

Three small switches control the buttons around a form:

| Setting | Default | Controls |
| --- | --- | --- |
| `SHOW_HISTORY` | `True` | The "History" button at the top of the edit page. |
| `SHOW_VIEW_ON_SITE` | `True` | The "View on site" button, for models with `get_absolute_url()`. |
| `SHOW_BACK_BUTTON` | `True` | The small "back to the list" link above the title. It keeps the filters you had. |
