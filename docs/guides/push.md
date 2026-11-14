# Web Push

Web Push delivers notifications when the admin is not open: to a desktop browser that is running in the background, and to phones. Every [notification](notifications.md) can also go out as a push message. It uses the standard Web Push protocol with VAPID keys, so there is no third party service and no account to create.

## What you need

- The `push` extra, which installs `pywebpush`.
- HTTPS. Browsers only allow push on secure sites. `localhost` counts as secure, so you can try it during development.
- On iPhone and iPad (iOS 16.4 or newer), the admin has to be added to the home screen first. Safari does not allow push for normal tabs.

## Step by step

### 1. Install the extra

```bash
pip install "django-cc-admin[push]"
```

### 2. Make a key pair

```bash
python manage.py cc_admin_vapid
```

```text
Add these to CC_ADMIN['PUSH'] and keep the private key out of version control:

"vapid_public_key": "BMx3...",
"vapid_private_key": "q8Zf...",
"vapid_claims": {"sub": "mailto:you@example.com"},
```

Make the keys once and keep them. If you change them, every device has to turn push on again.

### 3. Add the keys to your settings

Keep the private key in the environment, not in the repository:

```python
import os

CC_ADMIN = {
    "PUSH": {
        "enabled": True,
        "vapid_public_key": os.environ["VAPID_PUBLIC_KEY"],
        "vapid_private_key": os.environ["VAPID_PRIVATE_KEY"],
        "vapid_claims": {"sub": "mailto:admin@example.com"},
        "icon": "img/push-icon.png",
        "badge": "img/push-badge.png",
        "ttl": 3600,
        "levels": None,
    },
}
```

`sub` should be a `mailto:` address or a URL where push services can reach you if something goes wrong.

If `enabled` is `True` but a key is missing, `python manage.py check` warns you (`cc_admin.W001`).

### 4. Turn push on in the browser

Each person turns push on for each of their devices: open the bell, open the settings, switch on push, and allow notifications when the browser asks. A "Send a test" button sends a notification to that device right away.

### 5. Send something

Every call to `notify()` and every rule now also sends a push, unless you pass `push=False`:

```python
notify("group:Warehouse", "Truck arrived", body="Dock 3, 14 pallets.", level="info", icon="truck")
```

## Settings

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `False` | Turn push on. |
| `vapid_public_key` | `""` | From `cc_admin_vapid`. Sent to browsers. |
| `vapid_private_key` | `""` | From `cc_admin_vapid`. Keep it secret. |
| `vapid_claims` | `{}` | Usually `{"sub": "mailto:you@example.com"}`. |
| `icon` | none | The large picture of the notification. A static path or URL. |
| `badge` | none | The small monochrome icon Android shows in the status bar. |
| `ttl` | `3600` | How long, in seconds, the push service keeps a message for a device that is offline. |
| `levels` | `None` | Only push these levels, for example `["warning", "danger"]`. `None` pushes every level. |

## How it works

- When a person turns push on, the browser registers a small service worker served at `/admin/cc/sw.js` and sends its subscription to `/admin/cc/push/subscribe/`. Each subscription is stored as a `PushSubscription` row, linked to the user.
- `notify()` sends to every subscription of every recipient in a background thread, so the request that triggered it does not wait for the push services.
- When a push service answers that a subscription is gone (HTTP 404 or 410), the row is deleted. Other errors are logged on the `cc_admin.notify` logger.
- Clicking the notification on the device opens its link, or focuses an admin tab that already shows it.
- A newer push with the same `key` replaces the older one on the device instead of stacking up.

Staff can see and remove subscriptions under "Push subscriptions" in the admin.

## Troubleshooting

**The push switch is missing in the bell settings.** Push is off in settings, the public key is empty, or the page is not on HTTPS.

**The browser says notifications are blocked.** The person blocked them for this site earlier. They have to allow them again in the browser's site settings.

**Nothing arrives on an iPhone.** Add the admin to the home screen, open it from there, and turn push on inside that app.

**Push works on one server but not another.** Each server needs the same keys. A different public key means the stored subscriptions do not match.
