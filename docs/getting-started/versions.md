# Supported versions

| django-cc-admin | Django | Python |
| --- | --- | --- |
| 0.1.0 | 5.0, 5.1, 5.2, 6.0, 6.1 | 3.10, 3.11, 3.12, 3.13 |

Django sets its own floor for Python: Django 5.0 to 5.2 run on Python 3.10 and newer, while Django 6.0 and 6.1 need Python 3.12 or newer. Pick a combination that Django itself supports.

The test suite runs the main admin pages in every theme, the list and form features, the live update endpoints and the notification rules. It passes on every Django version in the table.

## Databases

django-cc-admin uses the Django ORM only, with no raw SQL, so it works on every database Django supports: PostgreSQL, MySQL, MariaDB, SQLite and Oracle.

## Browsers

The admin is built for current versions of Chrome, Edge, Firefox and Safari, on desktop and on phones. A few features depend on what the browser allows:

| Feature | Needs |
| --- | --- |
| Desktop notifications | The user allows notifications for the site |
| Web Push | HTTPS (or `localhost`), a service worker, and on iPhone and iPad the admin added to the home screen |
| Sounds | The Web Audio API. Browsers only play sound after the user has clicked or typed on the page once |
| Live updates over `sse` | `EventSource`, which every current browser has |
| Live updates over `websocket` | WebSockets and an ASGI server |

When a feature is not available, the rest of the admin keeps working. Live updates fall back to polling when a stream or a socket keeps failing.

## Servers

The default setup needs nothing more than a normal WSGI deployment. The `sse` transport works on WSGI and ASGI but keeps one connection open per tab, so on WSGI use threaded or async workers. The `websocket` transport needs ASGI and Django Channels. See [Live updates](../guides/live-updates.md) and the [deployment recipe](../examples/deploy-daphne-nginx.md).
