# Installation

This page walks through installing django-cc-admin into an existing Django project. If you are starting from nothing, the [quickstart](quickstart.md) does the same steps inside a brand new project.

## What you need

- Python 3.10 or newer. Django 6.0 and 6.1 need Python 3.12 or newer.
- Django 5.0, 5.1, 5.2, 6.0 or 6.1. The package installs Django 5.0 or newer if you do not have it yet.
- A project that already uses `django.contrib.admin`.

Nothing else is required. The optional extras for WebSockets and Web Push are covered further down.

## 1. Make a virtual environment

If your project already has one, activate it and skip to step 2. Otherwise create one in the project folder, next to `manage.py`.

::::{tab-set}

:::{tab-item} Linux and macOS
```bash
cd ~/projects/mysite
python3 -m venv .venv
source .venv/bin/activate
```
:::

:::{tab-item} Windows (CMD)
```bat
cd %USERPROFILE%\projects\mysite
py -m venv .venv
.venv\Scripts\activate
```
:::
::::

The prompt now starts with `(.venv)`. Every `pip` and `python` command below runs inside that environment.

## 2. Install the package

::::{tab-set}

:::{tab-item} pip
```bash
pip install django-cc-admin
```
:::

:::{tab-item} uv
```bash
uv add django-cc-admin
```
:::

:::{tab-item} Poetry
```bash
poetry add django-cc-admin
```
:::

:::{tab-item} requirements.txt
```text
django-cc-admin==0.1.0
```

Then run `pip install -r requirements.txt`.
:::
::::

The wheel and the source archive of every version are also attached to the [GitHub releases](https://github.com/qiyascc/django-cc-admin/releases), if you need to install without access to PyPI.

### Optional extras

Two features need packages that most projects do not have. Install them only if you plan to use them.

| Extra | Installs | Needed for |
| --- | --- | --- |
| `live` | `channels>=4.0`, `daphne>=4.0` | The `websocket` transport for [live updates](../guides/live-updates.md). The default `poll` and the `sse` transports need nothing. |
| `push` | `pywebpush>=2.0` | [Web Push](../guides/push.md) to phones and closed browsers, and the `cc_admin_vapid` command. |
| `all` | all of the above | Both. |

```bash
pip install "django-cc-admin[live]"
pip install "django-cc-admin[push]"
pip install "django-cc-admin[all]"
```

The quotes matter in zsh, where square brackets have a meaning of their own. In bash and Windows CMD they do no harm.

## 3. Add the app

Open `settings.py` and put `cc_admin` **above** `django.contrib.admin`:

```python
INSTALLED_APPS = [
    "cc_admin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shop",
]
```

The order is important. django-cc-admin replaces the admin templates, and Django uses the first template it finds. If `cc_admin` comes after `django.contrib.admin`, the stock templates win and you see the old admin. The package registers a system check for this, so `python manage.py check` tells you right away:

```text
ERRORS:
?: (cc_admin.E001) cc_admin must come before django.contrib.admin in INSTALLED_APPS.
	HINT: Move 'cc_admin' above 'django.contrib.admin' so its templates win.
```

Make sure the `request` context processor is switched on. The Django admin needs it anyway and new projects have it by default:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

## 4. Leave your URLs alone

There is nothing to add to `urls.py`. django-cc-admin hooks into Django's `AdminSite` when the app loads and adds its own pages under the admin prefix: the activity pages at `/admin/cc/activity/`, the notification list at `/admin/cc/notifications/`, the endpoints the browser uses for search and live updates, and a small service worker for push. The full list is in [URLs](../reference/urls.md).

Your existing line stays as it is:

```python
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
```

This also works for a custom `AdminSite` subclass or a second admin site, because the change is made on the `AdminSite` class itself.

## 5. Run the migration

django-cc-admin stores notifications and push subscriptions in two small tables. Create them once:

```bash
python manage.py migrate
```

```text
Running migrations:
  Applying cc_admin.0001_initial... OK
```

Nothing else in the package touches your database schema. The activity pages read Django's own `LogEntry` table, and user preferences such as the theme live in cookies and in the browser.

## 6. Collect static files

During development `runserver` serves the CSS, JavaScript and fonts from the app folder on its own. For production run `collectstatic` as you do for any other app:

```bash
python manage.py collectstatic
```

If you use WhiteNoise, a CDN or an S3 bucket for static files, django-cc-admin needs no special treatment. All its assets live under `cc_admin/` in your static root.

## 7. Check that it worked

```bash
python manage.py check
python manage.py runserver
```

Open `http://127.0.0.1:8000/admin/` and sign in with a staff account. You should see:

- the new sign in page, split into a picture side and a form side,
- after signing in, a dashboard with a greeting, the date and a card with your models,
- a sidebar on the left with a filter box and an icon next to every model,
- a theme name at the bottom of the sidebar; click it, or press {kbd}`t`, to open the appearance panel,
- a search box at the top that opens the command palette.

```{image} ../screenshots/aurora-light.jpg
:alt: The Aurora theme: dashboard, order list and product form
```

If you still see the stock admin, go back to step 3. If pages look unstyled, the static files are not being served; see the [FAQ](../reference/faq.md).

## What next

- Give the admin your name and logo: [Branding](../guides/branding.md).
- Pick a default theme or make your own: [Themes](../guides/themes.md) and [Colours, fonts and corners](../guides/appearance.md).
- Put real numbers on the dashboard: [Dashboard](../guides/dashboard.md).
- Use the extended `ModelAdmin` where it helps: [ModelAdmin extras](../guides/model-admin.md).
