# django-cc-admin

django-cc-admin is a new skin and a set of tools for the Django admin. You add one app to `INSTALLED_APPS` and the admin you already have gets a new look, a dashboard, a command palette, live updates, notifications and keyboard shortcuts. Your `ModelAdmin` classes keep working as they are. When you want more, you swap in `cc_admin.admin.ModelAdmin` for the models that need it and get row actions, better filters, expandable rows, drag and drop sorting and export.

```{image} screenshots/dashboard.jpg
:alt: The dashboard of the example shop in the Aurora theme
```

Version {{ version }} works with Django 5.0, 5.1, 5.2, 6.0 and 6.1 on Python 3.10 and newer. Everything it needs ships in the package: fifteen themes, fifteen fonts and more than two thousand Lucide icons. Nothing is loaded from a CDN.

```bash
pip install django-cc-admin
```

## Where to start

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Installation
:link: getting-started/installation
:link-type: doc

A virtual environment, the package, the right place in `INSTALLED_APPS`, one migration and a quick check that it all worked.
:::

:::{grid-item-card} Quickstart
:link: getting-started/quickstart
:link-type: doc

From `django-admin startproject` to a themed admin with a dashboard, a sidebar and a list with row actions, step by step.
:::

:::{grid-item-card} Themes and appearance
:link: guides/themes
:link-type: doc

The fifteen themes, the switcher every user gets, and how to change colours, fonts and corners or build a theme of your own.
:::

:::{grid-item-card} Dashboard
:link: guides/dashboard
:link-type: doc

A twelve column grid of KPIs, charts, tables, lists, heatmaps and activity calendars, all described in settings.
:::

:::{grid-item-card} ModelAdmin extras
:link: guides/model-admin
:link-type: doc

Badges, avatars and progress bars in list columns, tabs and a sticky side column in forms, fields that appear on a condition.
:::

:::{grid-item-card} Live updates and notifications
:link: guides/live-updates
:link-type: doc

Lists and forms that stay current without a reload, a notification bell with popups and sounds, and Web Push to phones.
:::

:::{grid-item-card} Recipes
:link: examples/shop-admin
:link-type: doc

Longer worked examples: a shop admin, a live order dashboard, staff alerts from model changes, and a deployment behind nginx.
:::

:::{grid-item-card} Settings reference
:link: reference/settings
:link-type: doc

Every key of the `CC_ADMIN` setting with its type, its default and what it changes.
:::
::::

## What you get without writing any code

Once `cc_admin` is installed, every page of the admin changes. You do not need to touch your admin classes to get these:

- A new look in one of fifteen themes, with light, dark and automatic modes and three densities. Each user picks their own from the user menu or by pressing {kbd}`t`.
- A dashboard on the admin index page with counts for your models, recent changes and the records you opened lately.
- A sidebar with a filter box, icons for every model and a star to pin the models you use most.
- A command palette on {kbd}`Ctrl+K` (or {kbd}`⌘+K` on a Mac) that jumps to any model, searches records and adds new ones.
- Keyboard shortcuts for lists and forms, with a help dialog on {kbd}`?` where people can rebind them.
- Lists that pick up new and changed rows while you look at them, and a bar on the edit page when somebody else saves the same record.
- A notification bell, popups with sounds, and desktop notifications.
- A GitHub style activity page for every staff user, built from the admin log Django already keeps.
- CSV and JSON export, a column picker and a "Per page" menu on every list.

## How the documentation is organised

**Getting started** takes you from nothing to a working admin. **Guides** explain one area at a time, with the settings and the Python API for it. **Recipes** put several features together into something you would actually build. **Reference** lists every setting, template tag, URL, command and class, and is the place to look things up once you know your way around.

```{toctree}
:hidden:
:caption: Getting started

getting-started/installation
getting-started/quickstart
getting-started/upgrading
getting-started/versions
```

```{toctree}
:hidden:
:caption: Look and feel

guides/themes
guides/appearance
guides/branding
guides/navigation
guides/dashboard
```

```{toctree}
:hidden:
:caption: Lists and forms

guides/model-admin
guides/actions
guides/filters
guides/sections
guides/widgets
guides/export
```

```{toctree}
:hidden:
:caption: Working faster

guides/command-palette
guides/shortcuts
guides/activity
```

```{toctree}
:hidden:
:caption: Live and notifications

guides/live-updates
guides/notifications
guides/push
guides/announcements
```

```{toctree}
:hidden:
:caption: Extending

guides/custom-pages
guides/permissions
```

```{toctree}
:hidden:
:caption: Recipes

examples/shop-admin
examples/live-dashboard
examples/notify-from-code
examples/deploy-daphne-nginx
```

```{toctree}
:hidden:
:caption: Reference

reference/settings
reference/templates
reference/urls
reference/commands
reference/api
reference/faq
reference/changelog
```

```{toctree}
:hidden:
:caption: Project

project/development
project/about
```
