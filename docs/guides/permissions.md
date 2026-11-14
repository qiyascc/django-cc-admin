# Permissions

Many settings decide who sees something: a sidebar item, a dashboard widget, an announcement, a palette command, the activity of other people, the page for sending notifications. They all take the same kind of value, described here once.

## Values

| Value | Who passes |
| --- | --- |
| `"staff"` (or `True`, `"all"`, `"everyone"`) | Every active staff user. |
| `"superuser"` | Superusers. |
| `"group:Warehouse"` | Members of the group named Warehouse. |
| `"perm:shop.change_order"` | Users with that permission, directly, through a group, or as superusers. |
| `"none"` (or `None`, `False`, `"nobody"`, `"self"`) | Nobody. |
| a list | Anyone who passes at least one item of the list. |
| a callable | Whoever the callable returns `True` for. |
| a dotted path | The same, with the callable imported from that path. |

Users who are not signed in, or whose account is inactive, never pass.

```python
"permission": ["superuser", "group:Managers", "perm:billing.view_invoice"]
```

## Callables

A callable receives the request. A few settings pass more arguments, and those are listed with each setting. The callable only receives as many arguments as it accepts, so a function written for the request alone works everywhere.

```python
def is_on_shift(request):
    return request.user.groups.filter(name="Support").exists() and request.user.profile.on_shift


CC_ADMIN = {
    "SIDEBAR": {
        "navigation": [
            {"title": "Support", "permission": is_on_shift, "items": [
                {"title": "Open tickets", "icon": "life-buoy", "link": "admin:support_ticket_changelist"},
            ]},
        ],
    },
}
```

As a dotted path, the same function is written `"support.permissions.is_on_shift"`.

```{warning}
Any string that is not one of the words above and does not start with `group:` or `perm:` is imported as a dotted path. A typo such as `"stafff"` raises an `ImportError` when the page is drawn, which makes it easy to spot.
```

## Where permissions are used

| Setting | Key | Extra arguments for a callable |
| --- | --- | --- |
| `SIDEBAR["navigation"]` groups and items | `permission` | |
| `TABS` items | `permission` | |
| `DASHBOARD["widgets"]` | `permission` | |
| `ANNOUNCEMENTS` | `permission` | |
| `COMMAND_PALETTE["commands"]` | `permission` | |
| `SHORTCUTS["custom"]` | `permission` | |
| `SITE_DROPDOWN`, `USER_LINKS` | `permission` | |
| `ACTIVITY` | `view` | |
| `ACTIVITY` | `others` | the user whose activity is shown, on personal pages |
| `NOTIFICATIONS` | `broadcast` | |

## What permissions do not do

These settings only decide what is shown in the admin's frame. They do not protect your data. A hidden sidebar link to a list is still reachable by typing the address, so the model admin's own `has_view_permission()` and friends remain the real guard. Django's permission checks on lists, forms and actions work as they always have.

`@action(permissions=[...])` on the model admin side is described in [Actions](actions.md#permissions), and `permission_required` on custom pages in [Custom pages](custom-pages.md).
