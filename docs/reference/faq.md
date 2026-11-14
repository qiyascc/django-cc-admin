# FAQ and troubleshooting

## I still see the old admin

`cc_admin` has to come before `django.contrib.admin` in `INSTALLED_APPS`. Run `python manage.py check`; it reports `cc_admin.E001` when the order is wrong. Also check your own templates folder: a copy of an admin template that does not extend another one, for example an old `admin/base.html`, replaces the package's version. Prefer extending, as shown in [Templates](templates.md).

## The pages have no styling

The static files are not being served.

- In development, `django.contrib.staticfiles` must be in `INSTALLED_APPS` and `DEBUG` on.
- In production, run `python manage.py collectstatic` and make sure your web server or WhiteNoise serves `STATIC_ROOT`.
- Check the browser's developer tools for 404 errors on files under `/static/cc_admin/`.

## An icon does not show up, only a dot

The name is not in the bundled set. Lucide renames icons from time to time, and the package ships the names from when it was built. List the names that are close:

```python
from cc_admin import icons

sorted(name for name in icons.symbols() if "alert" in name or "triangle" in name)
```

For example, the warning triangle is called `triangle-exclamation-point` in the bundled set.

## A badge or dashboard value shows a dotted path as text, or raises ImportError

Dotted paths must point to an importable function, with at least a module and a name: `"shop.dashboard.revenue"`. In badges, any string containing a dot is treated as a dotted path. For a fixed label, use text without dots.

For permission values, any string that is not a known word and does not start with `group:` or `perm:` is imported as a dotted path, so a typo such as `"stafff"` raises `ImportError`.

## Live updates do not pick up changes made outside the admin

Changes from a shell, an API or a worker reach the admin through Django's cache. With the default local memory cache each process has its own counters, so another process never sees them. Configure a shared cache such as Redis, Memcached, the database cache or the file cache. New rows still show up without it, because the admin also compares the highest primary key. See [How changes are noticed](../guides/live-updates.md#how-changes-are-noticed).

`QuerySet.update()` and `bulk_create()` do not send model signals, so their edits are only noticed through new primary keys or the admin log.

## The WebSocket keeps failing and the dot stays amber

- Is `LIVE["transport"]` set to `"websocket"` and Channels installed? `python manage.py check` warns otherwise.
- Is the app served by an ASGI server (daphne, uvicorn) and not by a WSGI one?
- Does `asgi.py` route `cc_admin.routing.websocket_urlpatterns` inside `AuthMiddlewareStack`?
- Does your proxy pass the `Upgrade` and `Connection` headers for `/ws/`? See the [nginx recipe](../examples/deploy-daphne-nginx.md#6-nginx).

When the socket fails repeatedly, the browser falls back to polling, so the admin keeps working while you fix it.

## Server-Sent Events arrive in bursts

A proxy is buffering the stream. django-cc-admin sends `X-Accel-Buffering: no`, which nginx respects. For other proxies, turn buffering off for `/admin/cc/live/stream/`.

## No sound plays

Browsers only allow sound after the user has clicked or typed on the page once. Also check the notification settings under the bell: sounds may be off, do not disturb may be on, or the volume may be at zero.

## Desktop or push notifications do not appear

- The browser or the operating system may block notifications for the site. Check the site settings in the browser and the notification settings of the operating system.
- Push needs HTTPS, except on `localhost`.
- On iPhone and iPad, push only works from the home screen app. See [Web Push](../guides/push.md#troubleshooting).

## Can I use it with a custom AdminSite?

Yes. The package changes the `AdminSite` class itself, so subclasses and extra admin sites get the same pages. For custom pages that do not belong to a model, pass `admin_site=` to `AdminPageView.as_view()`.

## Can I use it with django-import-export, django-simple-history and similar packages?

Yes. Put `cc_admin.admin.ModelAdminMixin` first in the base classes:

```python
class BookAdmin(ModelAdminMixin, ImportExportModelAdmin):
    ...
```

Their buttons and pages render inside the new frame. Packages that ship their own copies of the main admin templates may need their templates checked, because the last template found wins.

## Does it work with Content Security Policy?

Yes. All assets are local. When Django or your middleware puts a CSP nonce on the request or in the template context, the package adds it to its inline scripts and styles. Use `{% cc_nonce %}` for your own inline tags.

## Does it slow the admin down?

The extra work per page is small: the settings are cached, icons are sent only when a page uses them, and charts are drawn as SVG on the server. What you add can cost more, mainly dashboard data functions, sidebar badges and list sections, which run on every page load. Keep those to cheap queries and cache the heavy ones.

## Can I turn parts off?

Almost everything can be switched off on its own:

```python
CC_ADMIN = {
    "THEME_SWITCHER": False,
    "SHORTCUTS": False,
    "ACTIVITY": False,
    "LIVE": False,
    "NOTIFICATIONS": False,
    "COMMAND_PALETTE": {"enabled": False},
    "LIST_EXPORT": False,
}
```

## Where do user preferences live?

In the browser. Theme, mode, density, accent, font, text size and corners are in the `cc_admin_prefs` cookie, and rows per page in `cc_admin_per`. Pinned models, recent records, chosen columns, folded menu groups, rebound shortcuts, notification settings and closed announcements are in local storage under keys starting with `cc-admin:`. Nothing of this is stored in your database.
