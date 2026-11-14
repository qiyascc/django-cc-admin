# Announcements

Announcements are messages for everyone who uses the admin: a new feature, planned downtime, a rule that changes on Friday. Each person sees an announcement until they close it, and then never again. They are set in settings, so they ship with a deploy and need no database.

```{image} ../screenshots/announcement.jpg
:alt: A modal announcement over the dashboard, with a warning banner behind it
```

```python
CC_ADMIN = {
    "ANNOUNCEMENTS": [
        {
            "id": "new-reports",
            "style": "modal",
            "tone": "accent",
            "icon": "sparkles",
            "title": "Reports are here",
            "text": "Weekly numbers now live under Reports.",
            "link": "admin:shop_order_reports",
            "link_text": "Open reports",
            "image": "img/reports.png",
        },
        {
            "id": "stocktake-2026-11",
            "style": "banner",
            "tone": "warning",
            "title": "Stocktake on Friday.",
            "text": "Product edits are locked from 18:00.",
            "start": "2026-11-10",
            "end": "2026-11-14",
            "permission": "group:Warehouse",
        },
    ],
}
```

## Keys

| Key | Default | Meaning |
| --- | --- | --- |
| `id` | required | A unique name. Announcements without an `id` are skipped. |
| `style` | `"banner"` | `"banner"` is a coloured strip at the top of every page. `"modal"` is a dialog in the middle of the screen. |
| `tone` | `"info"` | `info`, `success`, `warning`, `danger`, `accent` or `neutral`. |
| `icon` | by tone | A Lucide icon. Defaults to a megaphone for `info`, a party popper for `success`, a warning triangle for `warning` and a stop sign for `danger`. |
| `title` | `""` | The heading. |
| `text` | `""` | The message. |
| `link` | none | A URL name, path or URL for the main button. |
| `link_text` | "Take a look" | The text of that button. Without a `link`, it is the text of the button that closes a modal, which defaults to "Got it". |
| `image` | none | A picture at the top of a modal. A static path or URL. |
| `start` | none | The first day to show it, as `"YYYY-MM-DD"`. |
| `end` | none | The last day to show it. |
| `dismissible` | `True` | For modals with a link: whether to show a separate "Close" button. |
| `permission` | none | Who sees it. See [Permissions](permissions.md). |

`start` and `end` are compared with today's date in your project's time zone, and both days are included.

## Showing it again

Closing an announcement is remembered in the browser under its `id`. To show an updated message to everybody again, change the `id`, for example by adding a date: `"stocktake-2026-11"` becomes `"stocktake-2026-12"`.

Because the memory lives in the browser, someone who signs in on a new computer sees current announcements once more.

## Dynamic announcements

The list, and each item in it, may be a callable that takes the request. That lets you build announcements from the database:

```python
from django.utils import timezone

from .models import Maintenance


def announcements(request):
    window = Maintenance.objects.filter(ends_at__gte=timezone.now()).order_by("starts_at").first()
    if window is None:
        return []
    return [{
        "id": f"maintenance-{window.pk}",
        "style": "banner",
        "tone": "danger",
        "title": "Planned maintenance.",
        "text": f"The admin is read only from {window.starts_at:%H:%M} to {window.ends_at:%H:%M}.",
    }]


CC_ADMIN = {"ANNOUNCEMENTS": announcements}
```

Announcements are only shown to signed in staff users.
