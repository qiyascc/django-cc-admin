# Upgrading

django-cc-admin follows the usual pattern for Django apps: upgrade the package, run the migrations, collect the static files and restart.

## Step by step

1. Read the [changelog](../reference/changelog.md) for every version between the one you have and the one you want. Anything that needs your attention is listed there.

2. Upgrade the package:

   ::::{tab-set}
   :::{tab-item} pip
   ```bash
   pip install --upgrade django-cc-admin
   ```
   :::
   :::{tab-item} uv
   ```bash
   uv add --upgrade django-cc-admin
   ```
   :::
   :::{tab-item} Poetry
   ```bash
   poetry update django-cc-admin
   ```
   :::
   ::::

   If you installed extras, name them again, for example `pip install --upgrade "django-cc-admin[live,push]"`.

3. Check the version you ended up with:

   ```bash
   python -c "import cc_admin; print(cc_admin.__version__)"
   ```

4. Run the system checks and the migrations:

   ```bash
   python manage.py check
   python manage.py migrate
   ```

5. Collect the static files, so browsers get the new CSS and JavaScript:

   ```bash
   python manage.py collectstatic --noinput
   ```

   The admin links its CSS and JavaScript with `?v=<version>` on the end, so browsers fetch the new files after an upgrade instead of using a cached copy.

6. Restart your application server (gunicorn, uWSGI, daphne, uvicorn) so the new code is loaded.

## Pinning

In production, pin an exact version and upgrade on purpose:

```text
django-cc-admin==0.1.0
```

## What survives an upgrade

User preferences (theme, mode, density, accent, font, text size, corners, pinned models, chosen columns, rows per page, rebound shortcuts and notification settings) live in cookies and in the browser's local storage. They are not touched by an upgrade. Notifications and push subscriptions live in the database tables created by `cc_admin.0001_initial` and are kept.

## Removing the package

To go back to the stock admin:

1. Remove `"cc_admin"` from `INSTALLED_APPS` and delete the `CC_ADMIN` setting.
2. If you switched to `cc_admin.admin.ModelAdmin`, `cc_admin.filters` or `cc_admin.decorators`, change those imports back to `django.contrib.admin` and remove the options that only django-cc-admin knows (`actions_row`, `list_sections`, `conditional_fields` and so on).
3. If you set up the WebSocket route, remove `cc_admin.routing` from `asgi.py`.
4. Drop the two tables, either before removing the app with `python manage.py migrate cc_admin zero`, or by hand afterwards (`cc_admin_notification` and `cc_admin_pushsubscription`).
5. `pip uninstall django-cc-admin`.
