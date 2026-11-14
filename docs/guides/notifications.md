# Notifications

django-cc-admin has a notification system for your staff. A bell in the top bar collects every notification, new ones pop up in a corner of the screen with a short sound, and when the tab is in the background the browser can show a desktop notification instead. With [Web Push](push.md) switched on, they also reach phones and closed browsers.

Notifications are stored in the database, one row per person, so someone who was away still finds them in the bell.

```{image} ../screenshots/notification-bell.jpg
:alt: The notification bell open over the dashboard
```

## The bell and the popups

The bell shows the number of unread notifications. Opening it lists the latest ones with All and Unread tabs, "Mark all read", a link to the full list at `/admin/cc/notifications/` and, for people allowed to broadcast, "Send one".

A popup shows the icon, the title and the text, and a thin bar that counts down until it closes. Hovering stops the countdown. Clicking it opens the link and marks the notification read. Up to `max` popups are shown at once.

Sounds are made in the browser with the Web Audio API, so there are no audio files to serve. The available sounds are `chime`, `pop`, `ping`, `bell`, `alert`, `sparkle`, `blip`, `cash`, `knock` and `none`.

## Sending a notification from code

```python
from cc_admin.notify import notify

notify(
    "staff",
    "Stock is low",
    body="Only 3 desks left.",
    link="/admin/shop/product/12/change/",
    level="warning",
    icon="package",
    sound="bell",
)
```

`notify()` takes:

| Argument | Default | Meaning |
| --- | --- | --- |
| `to` | required | Who gets it. See below. |
| `title` | required | The first line, up to 200 characters. |
| `body` | `""` | More text under the title. |
| `link` | `""` | Where a click goes: a path or a full URL. |
| `level` | `"info"` | `info`, `success`, `warning`, `danger`, `accent` or `neutral`. Sets the colour, the default icon and the default sound. An unknown level becomes `info`. |
| `icon` | level icon | A Lucide icon name. Unknown names fall back to the level's icon. |
| `sound` | level sound | One of the sounds above. |
| `actor` | `None` | The user who caused it. Shown with the notification. |
| `key` | `""` | A short label for the kind of notification. Push uses it as the tag, so a newer push with the same key replaces the older one on the phone. |
| `data` | `{}` | Any JSON you want to keep with the notification. |
| `push` | `True` | Also send it as a Web Push, if push is enabled. |
| `exclude_actor` | `False` | Leave the actor out of the recipients. |

It returns the list of `Notification` rows it created, and an empty list when notifications are disabled or nobody matched. It saves all rows with one `bulk_create`, tells open admin pages to check right away, and sends push messages in a background thread, so it is safe to call from a request.

### Recipients

`to` accepts:

| Value | Who |
| --- | --- |
| a user | That user. |
| a user id | The user with that primary key. |
| a queryset of users | Those users. |
| `"staff"` (or `"all"` or `True`) | Every active staff user. |
| `"superuser"` | Every active superuser. |
| `"group:Warehouse"` | Every active member of the group. |
| `"user:leyla"` | The user with that username. |
| `"perm:shop.change_order"` | Superusers, plus staff users who have the permission directly or through a group. |
| a list | Everyone matched by any item in the list. |
| a callable | Whatever the callable returns, with no arguments. |
| a dotted path | A callable imported from that path. |

Inactive users never receive notifications.

```python
notify(["group:Warehouse", "user:aysel"], "Stocktake tomorrow", body="Product edits lock at 18:00.", level="info", icon="calendar")
notify(order.assigned_to, f"{order.number} was assigned to you", link=f"/admin/shop/order/{order.pk}/change/")
```

## Notifications from model changes

Rules send notifications automatically when a model is created, updated or deleted, without touching your models or views:

```python
CC_ADMIN = {
    "NOTIFICATIONS": {
        "rules": [
            {
                "model": "shop.order",
                "on": "created",
                "title": "New order {obj.number}",
                "body": "{obj.customer} · ${obj.total}",
                "level": "success",
                "icon": "receipt",
                "sound": "cash",
            },
            {
                "model": "shop.order",
                "on": "updated",
                "when": "shop.notifications.refunded",
                "title": "{obj.number} was refunded",
                "to": "superuser",
                "level": "danger",
            },
            {
                "model": "shop.product",
                "on": ["updated", "deleted"],
                "to": "group:Warehouse",
                "title": "{model} {event}: {obj}",
            },
        ],
    },
}
```

| Key | Default | Meaning |
| --- | --- | --- |
| `model` | required | `"app_label.modelname"`. |
| `on` | `"created"` | `"created"`, `"updated"`, `"deleted"`, or a list of them. |
| `title` | `"{model} {event}"` | The title. See placeholders below. |
| `body` | `""` | The text. |
| `to` | `"staff"` | Recipients, as for `notify()`. A callable here receives the object. |
| `when` | none | A callable, or dotted path, that receives `(obj, event)` and returns whether to send. |
| `link` | `"change"` | `"change"` for the object's edit page (the list for deletions), `"list"` for the list, a URL or URL name, or a callable that receives the object. |
| `level`, `icon`, `sound` | as `notify()` | |
| `push` | `True` | Also send a Web Push. |
| `exclude_actor` | `True` | Do not tell people about their own changes. |
| `key` | `"app.model:event"` | As for `notify()`. |

`title` and `body` are Python format strings with four names:

- `{obj}`: the object, so `{obj.number}` or `{obj.customer.name}` work,
- `{actor}`: the user who made the change, or empty when there is none,
- `{event}`: `created`, `updated` or `deleted`,
- `{model}`: the model's verbose name.

They can also be callables that receive `(obj, event)` and return the text.

### Reacting to one field changing

A rule on `"updated"` fires on every save. To fire only when a field changes, remember the old value when the object is loaded and compare in `when`. The example project does it like this:

```python
class Order(models.Model):
    @classmethod
    def from_db(cls, db, field_names, values):
        obj = super().from_db(db, field_names, values)
        obj.tracker_status = obj.__dict__.get("status")
        return obj
```

```python
def refunded(order, event):
    return order.status == "refunded" and getattr(order, "tracker_status", None) != "refunded"
```

### Who is the actor

Inside admin views the actor is the signed in user, which is how `exclude_actor` knows not to notify you about your own change. Outside the admin (a shell, a worker, your own views) there is no actor, so everyone in `to` is notified.

Rules run on `post_save` and `post_delete`. Saves done while loading fixtures are skipped. Bulk operations such as `QuerySet.update()` do not send those signals, so rules do not see them. A rule that raises an error is logged on the `cc_admin.notify` logger and does not break the save.

## Sending from the admin

Superusers get a page at `/admin/cc/notifications/send/` to message everyone, a group or one person, pick the style and the sound, and push it to phones. "Send one" in the bell and a button on the Notifications list lead there.

```{image} ../screenshots/send-notification.jpg
:alt: The send a notification form
```

Who may use it is set by `broadcast`.

## Settings

```python
CC_ADMIN = {
    "NOTIFICATIONS": {
        "enabled": True,
        "bell": True,
        "popup": True,
        "position": "bottom-right",
        "duration": 7,
        "max": 4,
        "sound": "chime",
        "sounds": {"success": "chime", "info": "pop", "warning": "bell", "danger": "alert", "accent": "sparkle", "neutral": "blip"},
        "volume": 0.6,
        "desktop": True,
        "desktop_when": "hidden",
        "user_settings": True,
        "broadcast": "superuser",
        "keep_days": 60,
        "admin": True,
        "rules": [],
    },
}
```

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `True` | Turn the whole system off. `notify()` then does nothing and returns an empty list. |
| `bell` | `True` | Show the bell in the top bar. |
| `popup` | `True` | Show popups for new notifications. |
| `position` | `"bottom-right"` | `top-right`, `top-center`, `top-left`, `bottom-right`, `bottom-center` or `bottom-left`. |
| `duration` | `7` | Seconds a popup stays. `0` keeps it until closed. |
| `max` | `4` | Popups shown at once. |
| `sound` | `"chime"` | The fallback sound. |
| `sounds` | per level | The sound for each level, used when a notification has none of its own. |
| `volume` | `0.6` | From 0 to 1. |
| `desktop` | `True` | Offer desktop notifications. The browser asks for permission the first time. |
| `desktop_when` | `"hidden"` | `"hidden"` only uses desktop notifications while the tab is in the background. `"always"` uses them even when it is open. |
| `user_settings` | `True` | Let each person change their own notification settings. |
| `broadcast` | `"superuser"` | Who may use the send page. A [permission](permissions.md) value. |
| `keep_days` | `60` | How old notifications get before `cc_admin_cleanup` deletes them. |
| `admin` | `True` | Register the Notifications and Push subscriptions models in the admin. |
| `rules` | `[]` | The rules described above. |

## Each person's own settings

With `user_settings` on, the settings button in the bell lets each person:

- turn popups and sounds on or off, and pick a sound and the volume,
- allow desktop notifications,
- turn push on for the current device and send themselves a test,
- switch on "do not disturb" for an hour, four hours or until tomorrow,
- pause live updates.

These choices are kept in their browser.

## Cleaning up

Every notification is a row per recipient, so the table grows. Delete old ones from cron:

```bash
python manage.py cc_admin_cleanup
```

```text
1284 notifications deleted.
```

It deletes notifications older than `keep_days`. With `keep_days` set to `0` or `None`, it deletes nothing.

## The models

`cc_admin.models.Notification` has `recipient`, `actor`, `title`, `body`, `link`, `level`, `icon`, `sound`, `key`, `data`, `created_at` and `read_at`. You can query it like any model, for example to show unread counts elsewhere:

```python
from cc_admin.models import Notification

Notification.objects.filter(recipient=request.user, read_at__isnull=True).count()
```

To mark notifications read from code, use `cc_admin.notify.mark_read(user, ids=None)`. Without `ids` it marks all of the user's notifications.

In the admin, the Notifications list has filters for level and read state, and "Mark as read" and "Mark as unread" actions. Set `"admin": False` to hide both models from the admin.
