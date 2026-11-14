# Management commands and checks

## cc_admin_cleanup

Deletes notifications older than `NOTIFICATIONS["keep_days"]` (60 days by default).

```bash
python manage.py cc_admin_cleanup
```

```text
1284 notifications deleted.
```

With `keep_days` set to `0` or `None` it deletes nothing. Run it from cron, once a day or once a week:

```text
30 3 * * * cd /srv/shop && .venv/bin/python manage.py cc_admin_cleanup
```

## cc_admin_vapid

Makes a VAPID key pair for [Web Push](../guides/push.md) and prints it ready to paste into settings.

```bash
python manage.py cc_admin_vapid
```

```text
Add these to CC_ADMIN['PUSH'] and keep the private key out of version control:

"vapid_public_key": "BMx3...",
"vapid_private_key": "q8Zf...",
"vapid_claims": {"sub": "mailto:you@example.com"},
```

It needs the `push` extra (`pip install "django-cc-admin[push]"`) and stops with a message if `cryptography` is missing. Each run makes a new pair; keep the first one you use, because changing keys means every device has to turn push on again.

## System checks

django-cc-admin registers three checks that run with `python manage.py check` and before `runserver` and `migrate`.

| ID | Level | When | Fix |
| --- | --- | --- | --- |
| `cc_admin.E001` | Error | `cc_admin` comes after `django.contrib.admin` in `INSTALLED_APPS`. | Move `cc_admin` above `django.contrib.admin`. |
| `cc_admin.W001` | Warning | `PUSH["enabled"]` is `True` but a VAPID key is missing. | Run `cc_admin_vapid` and copy the keys into `CC_ADMIN["PUSH"]`. |
| `cc_admin.W002` | Warning | `LIVE["transport"]` is `"websocket"` but Channels is not installed. | `pip install "django-cc-admin[live]"`, or use `"poll"` or `"sse"`. |

To silence a warning you have decided to live with:

```python
SILENCED_SYSTEM_CHECKS = ["cc_admin.W002"]
```

## Commands of the example project

The example project in the repository has two more commands, which are not part of the package:

`python manage.py seed [--orders 2200] [--seed 7]`
: Fills the example shop with products, customers, orders and a year of admin history for a small team.

`python manage.py simulate [--every 8] [--count 0]`
: Keeps placing fake orders, so you can watch live updates and notifications.
