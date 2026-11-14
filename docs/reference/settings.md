# Settings reference

Everything is configured through one dict in your Django settings, `CC_ADMIN`. Every key is optional. Keys you leave out take the defaults below.

```python
CC_ADMIN = {
    "SITE_HEADER": "Northwind",
    "THEME": "aurora",
}
```

Settings are read once and cached. In tests, `override_settings(CC_ADMIN=...)` clears that cache, so overrides work as expected.

## Kinds of values

Some keys accept more than a plain value:

Callable
: A function that takes the request. It is called on every page.

Dotted path
: A string such as `"shop.dashboard.revenue"`, imported the first time it is used and then called with the request.

Link
: A URL name (`"admin:shop_order_changelist"`), a path (`"/admin/shop/order/"`), a full URL, or a value starting with `#`, `?` or `mailto:`. A string that is not a path and cannot be reversed as a URL name is used as it is.

Asset
: A static path such as `"img/logo.svg"` (resolved with `{% static %}`), an absolute path, a full URL or a `data:` URL.

Permission
: A rule such as `"staff"`, `"superuser"`, `"group:Name"` or `"perm:app.codename"`, a list of them, a callable or a dotted path. See [Permissions](../guides/permissions.md).

The "Callable" column below says whether a key accepts a callable or dotted path. Keys marked "no" must be plain values.

## Site

| Key | Default | Callable | Meaning |
| --- | --- | --- | --- |
| `SITE_HEADER` | `None` | yes | The name in the corner. Falls back to `admin.site.site_header`. |
| `SITE_SUBHEADER` | `None` | yes | A line under the name. |
| `SITE_TITLE` | `None` | yes | The end of the browser tab title. Falls back to `admin.site.site_title`. |
| `SITE_URL` | `None` | yes | The "View site" link. Falls back to `admin.site.site_url`. |
| `SITE_LOGO` | `None` | yes | An asset, or `{"light": ..., "dark": ...}`. Replaces the brand square and name. |
| `SITE_ICON` | `None` | yes | An asset, or `{"light": ..., "dark": ...}`, shown in the brand square. |
| `SITE_FAVICON` | `None` | yes | An asset. |
| `SITE_SYMBOL` | `None` | yes | A Lucide icon name for the brand square. |
| `SITE_DROPDOWN` | `[]` | yes | Links in a menu next to the brand: `title`, `icon`, `link`, `new_tab`, `permission`. |
| `ENVIRONMENT` | `None` | yes | A badge in the top bar: a string, `(label, tone)` or `{"label", "tone"}`. |
| `ENVIRONMENT_TITLE_PREFIX` | `False` | no | `True` puts `[Label]` in front of tab titles. A string is used as the prefix. |
| `LOGIN` | `{}` | partly | The sign in page: `title` (callable), `text` (callable), `image` (asset). |
| `USER_LINKS` | `[]` | yes | Extra links in the user menu: `title`, `icon`, `link`, `permission`. |
| `FOOTER` | `None` | yes | Text for the page footer. Escaped unless you return a safe string. |
| `SHOW_LANGUAGES` | `False` | no | A language menu. Needs `django.conf.urls.i18n` in your URLs. |
| `SHOW_HISTORY` | `True` | no | The "History" button on edit pages. |
| `SHOW_VIEW_ON_SITE` | `True` | no | The "View on site" button. |
| `SHOW_BACK_BUTTON` | `True` | no | The "back to the list" link above edit pages. |
| `STYLES` | `[]` | items | Extra stylesheets, as assets. |
| `SCRIPTS` | `[]` | items | Extra scripts, as assets. Loaded with `defer`. |

See [Branding and the site frame](../guides/branding.md).

## Look

| Key | Default | Callable | Meaning |
| --- | --- | --- | --- |
| `THEME` | `"aurora"` | no | The default theme. |
| `THEMES` | `None` | no | Changes to built in themes and new themes. See below. |
| `THEME_ORDER` | `None` | no | A list of theme keys to show first in the switcher. |
| `THEME_SWITCHER` | `True` | no | Let users pick theme, mode, density and appearance. |
| `LAYOUT` | `None` | no | Force `sidebar`, `topbar`, `rail` or `float` for every theme. |
| `COLOR_SCHEME` | `"auto"` | no | `auto`, `light` or `dark`. |
| `DENSITY` | `"comfortable"` | no | `compact`, `comfortable` or `spacious`. |
| `COLORS` | `{}` | no | Friendly colour names. Nested `light` and `dark` dicts apply to one mode. |
| `FONTS` | `True` | no | `{"body", "heading", "mono", "size", "files", "bundled"}`, or `False` to skip the bundled fonts. |
| `RADIUS` | `None` | no | `sharp`, `soft`, `round`, `default`, a number of pixels or a CSS length. |
| `TOKENS` | `{}` | no | Raw CSS custom properties without the `--cc-` prefix. Nested `light` and `dark` dicts apply to one mode. |
| `APPEARANCE` | see below | no | What users may change in the appearance panel. `False` hides those controls. |

See [Themes](../guides/themes.md) and [Colours, fonts and corners](../guides/appearance.md).

### COLORS keys

`accent`, `accent_hover`, `on_accent`, `accent_text`, `background`, `background_2`, `surface`, `surface_2`, `surface_3`, `border`, `border_strong`, `text`, `text_muted`, `text_subtle`, `success`, `warning`, `danger`, `info`, `sidebar`, `sidebar_text`, `sidebar_active`, `sidebar_active_text`, `topbar`, `input`, `heatmap` and `chart` (a list of up to six colours). Any other key is used as a raw token name.

### THEMES entries

```python
"THEMES": {
    "<key>": {
        "extends": "aurora",
        "label": "...",
        "note": "...",
        "colors": {},
        "fonts": {},
        "radius": None,
        "tokens": {},
        "dark": {},
        "layout": "sidebar",
        "scheme": "auto",
        "density": "comfortable",
        "schemes": ["light", "dark"],
        "swatch": ["#page", "#card", "#accent", "#text"],
        "enabled": True,
    },
}
```

A key that names a built in theme changes it. Any other key creates a new theme based on `extends`.

### APPEARANCE

| Key | Default |
| --- | --- |
| `accent` | `True` |
| `accents` | `["#5b5bd6", "#2563eb", "#0e8a8a", "#16a34a", "#d97706", "#e5484d", "#db2777", "#7c3aed", "#18181b"]` |
| `font` | `True` |
| `fonts` | `None`, which offers Geist, Manrope, DM Sans, Figtree, Plus Jakarta Sans, IBM Plex Sans, Nunito, Archivo, Space Grotesk, Source Serif 4, JetBrains Mono and System |
| `font_size` | `True` |
| `radius` | `True` |

## Navigation

### SIDEBAR

| Key | Default | Meaning |
| --- | --- | --- |
| `search` | `True` | The filter box. |
| `show_all_applications` | `True` | List all apps after your own groups. |
| `pinned` | `True` | Allow pinning models. |
| `icons` | `{}` | Icons for `"app.model"` and `"app"` keys. |
| `navigation` | `[]` | Your groups. Each group: `title`, `icon`, `items`, `collapsible`, `permission`, `key`. Each item: `title`, `icon`, `link`, `badge`, `badge_variant`, `permission`, `active`. Groups may be callables. |

### TABS

A list of tab groups. Each group has `models` (a list of `"app.model"`), `pages` (a list of links) and `items` (each with `title`, `icon`, `link`, `badge`, `permission`, `active`). The first group that matches the page is shown.

See [Sidebar, tabs and icons](../guides/navigation.md).

## Dashboard

### DASHBOARD

| Key | Default | Callable | Meaning |
| --- | --- | --- | --- |
| `greeting` | `True` | no | The date and "Good morning" line. |
| `title` | `None` | yes | A heading that replaces the greeting text. |
| `subtitle` | `None` | yes | A line under it. |
| `callback` | `None` | yes | `(request, context)`, returns a dict added to the context. |
| `widgets` | `None` | yes | The widgets. `None` shows the default three. |

Widget types: `kpi`, `chart`, `table`, `list`, `progress`, `links`, `heatmap`, `models`, `activity`, `recent`, `contributions`, `team`, `cohort`, `tracker`, `note`, `html` (also `template`) and `apps`. Every widget takes `title`, `subtitle`, `icon`, `width`, `link`, `link_text` and `permission`. See [Dashboard](../guides/dashboard.md) for the keys of each type.

## Lists and forms

| Key | Default | Meaning |
| --- | --- | --- |
| `LIST_EXPORT` | `True` | CSV and JSON export on lists of `cc_admin.admin.ModelAdmin`. |
| `LIST_PER_PAGE_OPTIONS` | `[25, 50, 100, 200]` | Choices for the "Per page" menu. |
| `WARN_UNSAVED_FORMS` | `True` | Ask before leaving a changed form. |
| `FORMS` | see below | Form defaults. |

### FORMS

| Key | Default | Meaning |
| --- | --- | --- |
| `switches` | `False` | Toggle switches for every `BooleanField`. |
| `json_editor` | `True` | The JSON widget for every `JSONField`. |
| `show_cancel` | `True` | A "Cancel" button in the save bar. |
| `char_counter` | `True` | Character counters on inputs with a `max_length`. |

See [ModelAdmin extras](../guides/model-admin.md).

## Working faster

### COMMAND_PALETTE

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `True` | The palette and the search box in the top bar. |
| `search_models` | `True` | Search records through each model admin's `search_fields`. |
| `limit` | `5` | Records per model, 1 to 25. |
| `min_length` | `2` | Characters before records are searched. |
| `commands` | `[]` | Extra entries: `title`, `subtitle`, `icon`, `link`, `keywords`, `group`, `permission`. |
| `search_callback` | `None` | `(request, query)`, returns a list of `{"title", "subtitle", "icon", "link"}`. |

### SHORTCUTS

`False` turns shortcuts off. Otherwise a dict:

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `True` | Keyboard shortcuts and the help dialog. |
| `user_editable` | `True` | Let users rebind keys in the help dialog. |
| `keys` | `{}` | New keys for built in actions. `None` turns one off. |
| `custom` | `[]` | Your own shortcuts: `keys`, `title`, `link`, `new_tab`, `click`, `permission`, `scope`, `id`. |

Action names: `palette`, `help`, `search`, `dashboard`, `activity`, `site`, `theme`, `menu`, `next_row`, `prev_row`, `select_row`, `select_all`, `open_row`, `open_row_tab`, `expand_row`, `add`, `filters`, `columns`, `export`, `prev_page`, `next_page`, `save`, `save_continue`, `save_add`, `next_tab`, `prev_tab`, `history`, `back`, `delete`. See [Keyboard shortcuts](../guides/shortcuts.md) for the defaults.

### ACTIVITY

`False` turns the activity pages off. Otherwise a dict:

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `True` | The pages, the menu entry and the widgets. |
| `view` | `"staff"` | Permission to open the activity pages. |
| `others` | `"superuser"` | Permission to see other people. A callable also gets the person. |
| `team` | `True` | The team page at `/admin/cc/activity/`. |
| `details` | `True` | Record names and change messages. |
| `weeks` | `53` | Length of the calendar. |
| `exclude` | `[]` | `"app.model"` labels to leave out. |
| `menu` | `True` | "Activity" in the sidebar. |

See [Activity pages](../guides/activity.md).

## Live and notifications

### LIVE

`False` turns live updates off. Otherwise a dict:

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `True` | Live updates for staff users. |
| `transport` | `"poll"` | `poll`, `sse` or `websocket`. |
| `url` | `"/ws/cc-admin/"` | The WebSocket path. |
| `interval` | `5` | Seconds between checks in a visible tab. |
| `hidden_interval` | `30` | Seconds between checks in a background tab. |
| `stream_seconds` | `25` | Length of one Server-Sent Events connection. |
| `lists` | `"auto"` | `"auto"`, `"banner"` or `False`. |
| `forms` | `True` | The "someone else saved this" bar. |
| `presence` | `True` | Who else has the record open. |
| `dashboard` | `True` | Redraw the dashboard. |
| `dashboard_interval` | `30` | Minimum seconds between dashboard redraws. |
| `badges` | `True` | Keep sidebar and tab badges in sync. |
| `highlight` | `True` | Flash new and changed rows. |

See [Live updates](../guides/live-updates.md).

### NOTIFICATIONS

`False` turns notifications off. Otherwise a dict:

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `True` | The whole notification system. |
| `bell` | `True` | The bell in the top bar. |
| `popup` | `True` | Popups for new notifications. |
| `position` | `"bottom-right"` | `top-right`, `top-center`, `top-left`, `bottom-right`, `bottom-center`, `bottom-left`. |
| `duration` | `7` | Seconds a popup stays. `0` keeps it. |
| `max` | `4` | Popups shown at once. |
| `sound` | `"chime"` | Fallback sound. |
| `sounds` | `{"success": "chime", "info": "pop", "warning": "bell", "danger": "alert", "accent": "sparkle", "neutral": "blip"}` | Sound per level. Keys you give are merged into these. |
| `volume` | `0.6` | 0 to 1. |
| `desktop` | `True` | Offer desktop notifications. |
| `desktop_when` | `"hidden"` | `"hidden"` or `"always"`. |
| `user_settings` | `True` | Personal notification settings. |
| `broadcast` | `"superuser"` | Permission to use the send page. |
| `keep_days` | `60` | Age at which `cc_admin_cleanup` deletes notifications. |
| `admin` | `True` | Register the notification models in the admin. |
| `rules` | `[]` | Rules: `model`, `on`, `title`, `body`, `to`, `when`, `link`, `level`, `icon`, `sound`, `push`, `exclude_actor`, `key`. |

Sounds: `chime`, `pop`, `ping`, `bell`, `alert`, `sparkle`, `blip`, `cash`, `knock`, `none`. See [Notifications](../guides/notifications.md).

### PUSH

`False` or a dict:

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `False` | Web Push. |
| `vapid_public_key` | `""` | From `cc_admin_vapid`. |
| `vapid_private_key` | `""` | From `cc_admin_vapid`. Keep it secret. |
| `vapid_claims` | `{}` | Usually `{"sub": "mailto:..."}`. |
| `icon` | `None` | Asset for the notification picture. |
| `badge` | `None` | Asset for the small status bar icon. |
| `ttl` | `3600` | Seconds a push service keeps a message for an offline device. |
| `levels` | `None` | Only push these levels. |

See [Web Push](../guides/push.md).

### ANNOUNCEMENTS

A list (or a callable returning one) of dicts with `id` (required), `style` (`banner` or `modal`), `tone`, `icon`, `title`, `text`, `link`, `link_text`, `image`, `start`, `end`, `dismissible` and `permission`. See [Announcements](../guides/announcements.md).

## The full default

For reference, this is what django-cc-admin uses when `CC_ADMIN` is empty:

```python
CC_ADMIN = {
    "SITE_TITLE": None,
    "SITE_HEADER": None,
    "SITE_SUBHEADER": None,
    "SITE_URL": None,
    "SITE_LOGO": None,
    "SITE_ICON": None,
    "SITE_FAVICON": None,
    "SITE_SYMBOL": None,
    "SITE_DROPDOWN": [],
    "THEME": "aurora",
    "THEMES": None,
    "THEME_ORDER": None,
    "THEME_SWITCHER": True,
    "LAYOUT": None,
    "COLOR_SCHEME": "auto",
    "DENSITY": "comfortable",
    "FONTS": True,
    "COLORS": {},
    "RADIUS": None,
    "TOKENS": {},
    "APPEARANCE": {},
    "ENVIRONMENT": None,
    "ENVIRONMENT_TITLE_PREFIX": False,
    "STYLES": [],
    "SCRIPTS": [],
    "SIDEBAR": {},
    "TABS": [],
    "DASHBOARD": {},
    "COMMAND_PALETTE": {},
    "SHORTCUTS": {},
    "ACTIVITY": {},
    "LIVE": {},
    "NOTIFICATIONS": {},
    "PUSH": {},
    "ANNOUNCEMENTS": [],
    "LOGIN": {},
    "USER_LINKS": [],
    "FOOTER": None,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "SHOW_LANGUAGES": False,
    "WARN_UNSAVED_FORMS": True,
    "LIST_EXPORT": True,
    "LIST_PER_PAGE_OPTIONS": [25, 50, 100, 200],
    "FORMS": {},
}
```

The empty dicts are filled with the defaults listed in the tables above.
