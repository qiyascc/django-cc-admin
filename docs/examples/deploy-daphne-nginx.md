# Recipe: deploying with daphne behind nginx

This recipe puts a project with django-cc-admin into production on one Linux server, with WebSocket live updates, Web Push and HTTPS. It uses daphne as the ASGI server, nginx in front of it, Redis for the cache and the channel layer, and systemd to keep daphne running. The paths assume the project lives in `/srv/shop` and runs as the user `shop`.

If you do not need WebSockets, the default polling transport works with any WSGI setup you already have, and the [simpler variant](#variant-gunicorn-and-server-sent-events) at the end may be all you need.

## 1. Packages

```bash
cd /srv/shop
source .venv/bin/activate
pip install "django-cc-admin[all]" channels-redis
```

`[all]` brings Channels, daphne and pywebpush. `channels-redis` is the Redis channel layer. You also need a Redis server:

```bash
sudo apt install redis-server
```

## 2. Settings

```python
import os

DEBUG = False
ALLOWED_HOSTS = ["admin.example.com"]
CSRF_TRUSTED_ORIGINS = ["https://admin.example.com"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

INSTALLED_APPS = [
    "daphne",
    "cc_admin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shop",
]

ASGI_APPLICATION = "mysite.asgi.application"

STATIC_URL = "/static/"
STATIC_ROOT = "/srv/shop/static"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    },
}

CC_ADMIN = {
    "LIVE": {"transport": "websocket"},
    "PUSH": {
        "enabled": True,
        "vapid_public_key": os.environ["VAPID_PUBLIC_KEY"],
        "vapid_private_key": os.environ["VAPID_PRIVATE_KEY"],
        "vapid_claims": {"sub": "mailto:admin@example.com"},
    },
}
```

The shared Redis cache matters even with WebSockets: it is how a change made by one process, such as a background worker, reaches the pages served by another.

Make the push keys once with `python manage.py cc_admin_vapid` and put them in the environment file used below.

## 3. The ASGI application

`mysite/asgi.py`:

```python
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from cc_admin.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_app,
    "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns))),
})
```

`AllowedHostsOriginValidator` refuses WebSocket connections from pages on other sites.

## 4. Prepare the release

```bash
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput
```

## 5. Run daphne with systemd

`/etc/shop.env`, readable only by root and the `shop` user:

```text
DJANGO_SETTINGS_MODULE=mysite.settings
VAPID_PUBLIC_KEY=BMx3...
VAPID_PRIVATE_KEY=q8Zf...
```

`/etc/systemd/system/shop.service`:

```ini
[Unit]
Description=Shop admin (daphne)
After=network.target redis-server.service

[Service]
User=shop
Group=shop
WorkingDirectory=/srv/shop
EnvironmentFile=/etc/shop.env
ExecStart=/srv/shop/.venv/bin/daphne -b 127.0.0.1 -p 8001 mysite.asgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now shop
sudo systemctl status shop
```

## 6. nginx

`/etc/nginx/sites-available/shop`:

```nginx
upstream shop {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name admin.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name admin.example.com;

    ssl_certificate /etc/letsencrypt/live/admin.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.example.com/privkey.pem;

    client_max_body_size 20m;

    location /static/ {
        alias /srv/shop/static/;
        expires 30d;
        access_log off;
    }

    location /ws/ {
        proxy_pass http://shop;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 1h;
    }

    location / {
        proxy_pass http://shop;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/
sudo certbot certonly --nginx -d admin.example.com
sudo nginx -t
sudo systemctl reload nginx
```

The `/ws/` block is what makes WebSockets work: without the `Upgrade` and `Connection` headers, nginx turns the socket request into a plain HTTP request and the browser falls back to polling. If you changed `LIVE["url"]`, change the location to match.

The `http2 on;` line needs nginx 1.25.1 or newer. On older versions write `listen 443 ssl http2;` instead.

## 7. Check that it works

1. Open `https://admin.example.com/admin/` and sign in.
2. The dot in the top bar turns green. Hover it: "Live updates on".
3. In your browser's developer tools, the Network tab shows a WebSocket connection to `/ws/cc-admin/` with status 101.
4. Open the same order in two browsers. Save it in one; the other shows who changed it.
5. In the bell settings, switch on push and press "Send a test".

## 8. Background workers

Workers (Celery, django-q, RQ, cron jobs) can call `notify()` and save models like any other code. Two things make their changes appear live in the admin:

- the same Redis cache, so the change counters are shared, and
- the same channel layer, so the "something changed" nudge reaches the open sockets.

Both come from the settings above, as long as the workers use the same settings module.

## Variant: gunicorn and Server-Sent Events

If you prefer to stay on WSGI, Server-Sent Events give nearly the same experience without Channels:

```python
CC_ADMIN = {"LIVE": {"transport": "sse"}}
```

```ini
ExecStart=/srv/shop/.venv/bin/gunicorn mysite.wsgi:application --bind 127.0.0.1:8001 --workers 3 --worker-class gthread --threads 16 --timeout 60
```

Each open admin tab holds one thread for up to `stream_seconds` (25 by default) and then reconnects, so size `--threads` for the number of tabs your team keeps open. The stream sends `X-Accel-Buffering: no`, so the nginx `location /` block above works unchanged. Leave out the `/ws/` block, `daphne`, `ASGI_APPLICATION` and `CHANNEL_LAYERS`. Keep the Redis cache.
