# Changelog

## 0.2.1

Released on 2026-11-25.

- Project and author links point to qiyas.cc, the new address of the site. The description of the CC theme follows.

## 0.2.0

Released on 2026-11-22.

**Look**

- Volt, a dark theme with smoked glass panels over a warm backdrop, muted tile colours, lime pill buttons, underlined page titles and a soft blur as each page opens.
- New tones for cards, bars and columns: `blue`, `olive`, `rust`, `sand` and `plum`.

**Dashboard**

- KPI cards can be filled with their tone (`fill`), take any colour (`color`) and show progress towards a goal (`progress`, `progress_label`).
- Bar charts draw a target line (`target`, `target_label`), can highlight one bar (`highlight`) and grow in when the page loads.
- Progress widgets have a one line `row` layout for pipeline stages.
- A `forecast` widget with commit, likely and best case scenarios and the biggest items per period.

**Lists**

- A board view for any model with a status or stage field: columns per value, drag and drop or arrow keys to move cards, column counts and totals, the list's own filters, permission checks and history entries.

## 0.1.0

Released on 2026-11-12. The first public release.

**Look**

- Fifteen themes with four layouts (sidebar, top bar, icon rail, floating), light and dark modes and three densities, generated from one theme builder.
- An appearance panel for every user: theme, mode, density, accent colour, font, text size and corners, kept in a cookie so the page renders right on the first byte.
- `COLORS`, `FONTS`, `RADIUS`, `TOKENS` and per theme `THEMES` settings, including new themes built on top of existing ones.
- Fifteen bundled fonts and the Lucide icon set, with nothing loaded from a CDN.

**Admin frame**

- A dashboard built from settings with seventeen widget types and server side SVG charts.
- A sidebar with your own groups, live badges, pinning and icons guessed from model names.
- Tabs above related lists, an environment badge, a site switcher, user menu links, a redesigned sign in page and announcements.
- A command palette that searches records through the model admins' own search.
- Keyboard shortcuts for navigation, lists and forms, configurable in settings and rebindable by each user.
- A GitHub style activity page for the team and for each person, built from the admin log.

**Lists and forms**

- `cc_admin.admin.ModelAdmin` with list, row, detail and submit line actions, action groups, expandable rows, drag and drop sorting, CSV and JSON export, rows per page and a column picker.
- `@display` with badges, headers with avatars, copy buttons, tags, thumbnails and progress bars.
- Sixteen filters in a side panel with chips for active filters.
- Fieldset tabs, a sticky side column, conditional fields, compressed fields and inline tabs, collapsing and sorting.
- Switch, segmented, colour, rich text, code, JSON, image and counter widgets.
- `AdminPageView` for custom pages inside the admin frame.

**Live and notifications**

- Live lists, forms, presence, dashboards and badges over polling, Server-Sent Events or WebSockets.
- Notifications with a bell, popups, sounds, desktop notifications, rules on model changes and a page for sending them.
- Web Push with VAPID keys, the `cc_admin_vapid` and `cc_admin_cleanup` commands.

**Support**

- Django 5.0, 5.1, 5.2, 6.0 and 6.1 on Python 3.10 and newer.
