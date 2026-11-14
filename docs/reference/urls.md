# URLs

django-cc-admin adds its pages to every `AdminSite` when the app loads. You do not add anything to `urls.py`. The paths below assume the admin is mounted at `/admin/`; the URL names are in the admin's namespace, so `admin:cc_activity` for the default site.

## Site wide

| Path | Name | What it is |
| --- | --- | --- |
| `cc/activity/` | `cc_activity` | The team activity page. |
| `cc/activity/<user_id>/` | `cc_activity_user` | One person's activity. |
| `cc/notifications/` | `cc_notifications` | The full notification list. `?filter=unread` shows unread only, `?format=json` returns JSON. |
| `cc/notifications/read/` | `cc_notifications_read` | `POST` marks notifications read. Send `id` values, or none for all. |
| `cc/notifications/send/` | `cc_notifications_send` | The page for sending a notification. |
| `cc/search/` | `cc_search` | Record search for the command palette. `?q=` is the query. |
| `cc/live/` | `cc_live` | Live updates by polling. |
| `cc/live/stream/` | `cc_live_stream` | Live updates as Server-Sent Events. |
| `cc/push/subscribe/` | `cc_push_subscribe` | `POST` stores a push subscription. |
| `cc/push/unsubscribe/` | `cc_push_unsubscribe` | `POST` removes one. |
| `cc/push/test/` | `cc_push_test` | `POST` sends a test notification to the current user. |
| `cc/sw.js` | `cc_service_worker` | The service worker for Web Push. |

Every path except the service worker goes through `admin_view()`, so it needs a signed in staff user like any admin page.

```python
from django.urls import reverse

reverse("admin:cc_activity_user", args=[request.user.pk])
```

## Per model

Every model registered with `cc_admin.admin.ModelAdmin` (or the mixin) gets:

| Path | Name | What it is |
| --- | --- | --- |
| `<app>/<model>/cc-export/` | `<app>_<model>_cc_export` | Export of the current view. `?_format=csv` or `json`, plus any list filters. |
| `<app>/<model>/cc-sort/` | `<app>_<model>_cc_sort` | `POST` that saves a new row order for `ordering_field`. |
| `<app>/<model>/cc-action/<slug>/` | `<app>_<model>_cc_action` | Runs an `actions_list` action. |
| `<app>/<model>/<pk>/cc-action/<slug>/` | `<app>_<model>_cc_object_action` | Runs an `actions_row` or `actions_detail` action. |

## WebSocket

`cc_admin.routing.websocket_urlpatterns` holds one route, at the path from `LIVE["url"]` (`ws/cc-admin/` by default). Add it to your ASGI router as shown in [Live updates](../guides/live-updates.md#websockets).
