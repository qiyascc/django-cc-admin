# Live updates

With django-cc-admin, admin pages stay current while they are open. Nobody has to press reload to see a new order, and two people editing the same record find out about each other before one of them overwrites the other's work. It works without any setup through plain polling, on any server, and can be switched to Server-Sent Events or WebSockets when you want changes to arrive faster.

Live updates are only sent to signed in, active staff users.

## What updates

**Lists.** New and changed rows appear and flash briefly, and the record count, pagination and tab badges follow. If you are in the middle of something (rows selected, a menu open, a row expanded), the list does not change under your cursor. A small bar says "This list has new changes" instead, with a button to refresh when you are ready.

**The edit page.** When someone else saves the record you have open, a bar tells you who did it and which fields changed, with a reload button. If they deleted it, the bar turns red.

**Who else is here.** The edit page shows the other people who have the same record open, and whether they are only looking or have started editing.

**The dashboard.** Widgets are redrawn when the data behind them changes.

**Badges.** Sidebar and tab badges stay in sync with their counts.

**Notifications.** New notifications arrive in the bell and as popups. See [Notifications](notifications.md).

A small dot in the top bar shows the state of the connection: green and pulsing when live, amber while it reconnects, and grey when the user has paused live updates. Hover it to read the state.

## Settings

```python
CC_ADMIN = {
    "LIVE": {
        "enabled": True,
        "transport": "poll",
        "url": "/ws/cc-admin/",
        "interval": 5,
        "hidden_interval": 30,
        "stream_seconds": 25,
        "lists": "auto",
        "forms": True,
        "presence": True,
        "dashboard": True,
        "dashboard_interval": 30,
        "badges": True,
        "highlight": True,
    },
}
```

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `True` | Turn live updates off completely. `"LIVE": False` does the same. |
| `transport` | `"poll"` | `poll`, `sse` or `websocket`. See below. |
| `url` | `"/ws/cc-admin/"` | The WebSocket path, for the `websocket` transport. |
| `interval` | `5` | Seconds between checks while the tab is visible. |
| `hidden_interval` | `30` | Seconds between checks while the tab is in the background. |
| `stream_seconds` | `25` | How long one Server-Sent Events connection stays open before the browser opens a new one. |
| `lists` | `"auto"` | `"auto"` updates lists in place when it is safe and shows the bar otherwise. `"banner"` always shows the bar and never changes the list on its own. `False` turns list updates off. |
| `forms` | `True` | The "someone else saved this" bar on edit pages. |
| `presence` | `True` | Show who else has the record open. Needs `forms`. |
| `dashboard` | `True` | Redraw dashboard widgets. |
| `dashboard_interval` | `30` | The dashboard is redrawn at most once in this many seconds. |
| `badges` | `True` | Keep sidebar and tab badges in sync. |
| `highlight` | `True` | Flash new and changed rows. |

Each person can also pause live updates for themselves in the notification settings under the bell.

## Transports

All three transports send the same data. Only the way it travels differs.

| `transport` | How it works | What it needs |
| --- | --- | --- |
| `poll` | The browser asks a small JSON endpoint every `interval` seconds, less often in background tabs. | Nothing. Works on any server. |
| `sse` | Server-Sent Events. One open connection per tab that the server writes to. Each connection lasts `stream_seconds` and is then reopened. | Works on WSGI and ASGI. On WSGI each open tab holds a worker thread while connected, so use threaded workers (for example `gunicorn --threads 8`) or an ASGI server. |
| `websocket` | Django Channels. The server pushes a nudge the moment something changes and the browser fetches the details over the same socket. | `pip install "django-cc-admin[live]"`, an ASGI server, the routing below and a channel layer. |

If a stream or a socket keeps failing, the browser falls back to polling on its own.

### Server-Sent Events

```python
CC_ADMIN = {"LIVE": {"transport": "sse"}}
```

The stream endpoint sends `Cache-Control: no-cache` and `X-Accel-Buffering: no`, so nginx passes events through without buffering them. Other proxies may need buffering turned off for `/admin/cc/live/stream/`.

### WebSockets

1. Install the extra:

   ```bash
   pip install "django-cc-admin[live]"
   ```

2. Add Channels to your settings, choose a channel layer and set the transport:

   ```python
   INSTALLED_APPS = [
       "daphne",
       "cc_admin",
       "django.contrib.admin",
   ]

   ASGI_APPLICATION = "mysite.asgi.application"

   CHANNEL_LAYERS = {
       "default": {
           "BACKEND": "channels_redis.core.RedisChannelLayer",
           "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
       },
   }

   CC_ADMIN = {"LIVE": {"transport": "websocket"}}
   ```

   `channels_redis` is a separate package (`pip install channels-redis`). For a single process during development, `"BACKEND": "channels.layers.InMemoryChannelLayer"` works too, but it cannot reach other processes. Putting `"daphne"` first in `INSTALLED_APPS` makes `runserver` serve ASGI.

3. Route WebSockets in `mysite/asgi.py`:

   ```python
   import os

   from django.core.asgi import get_asgi_application

   os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
   django_app = get_asgi_application()

   from channels.auth import AuthMiddlewareStack
   from channels.routing import ProtocolTypeRouter, URLRouter

   from cc_admin.routing import websocket_urlpatterns

   application = ProtocolTypeRouter({
       "http": django_app,
       "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
   })
   ```

   Import `cc_admin.routing` after `get_asgi_application()`, because it needs Django to be set up.

4. Run an ASGI server, such as `daphne mysite.asgi:application` or `uvicorn mysite.asgi:application`.

If you set the transport to `websocket` without Channels installed, `python manage.py check` warns you (`cc_admin.W002`). The socket only accepts signed in, active staff users and closes with code 4403 for anyone else.

A complete production setup is in the [daphne and nginx recipe](../examples/deploy-daphne-nginx.md).

## How changes are noticed

django-cc-admin does not need you to call anything when data changes. It combines three signals:

1. **The admin log.** Every save and delete through the admin writes a `LogEntry`. Comparing the newest log entry per model tells whether a list or record changed, and who changed it.
2. **Model signals and the cache.** For changes made anywhere else (a shell, an API, a background worker), `post_save` and `post_delete` on every model registered in the admin bump a counter in Django's cache.
3. **The highest primary key.** Comparing the largest `pk` of each table catches new rows even without the cache. This is cached for two seconds per process.

The cache counter only works across processes if every process uses the same cache. Use Redis, Memcached, the database cache or the file based cache. The default `LocMemCache` lives inside one process, so with several gunicorn workers, changes made in one worker or a background job may only be noticed through the admin log and the primary key check: new rows still appear, but edits made outside the admin may not.

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    },
}
```

Bulk operations such as `QuerySet.update()` and `bulk_create()` do not send model signals, so their edits are only picked up through the admin log or new primary keys.

## The endpoints

| Path | Used by |
| --- | --- |
| `/admin/cc/live/` | The `poll` transport. |
| `/admin/cc/live/stream/` | The `sse` transport. |
| `/ws/cc-admin/` (the `url` setting) | The `websocket` transport. |

All of them answer only staff users.
