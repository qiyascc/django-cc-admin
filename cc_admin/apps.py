###############
# Qiyas Sadıqov CC
###############

import importlib.util

from django.apps import AppConfig
from django.conf import settings
from django.core import checks


class CCAdminConfig(AppConfig):
    name = "cc_admin"
    label = "cc_admin"
    verbose_name = "Notifications"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from . import live, notify, sites

        sites.install()
        live.connect()
        notify.connect()
        checks.register(check_order, checks.Tags.admin)
        checks.register(check_live)


def check_order(app_configs=None, **kwargs):
    apps = list(settings.INSTALLED_APPS)
    names = [a.split(".apps.")[0] for a in apps]
    if "cc_admin" in names and "django.contrib.admin" in names:
        if names.index("cc_admin") > names.index("django.contrib.admin"):
            return [
                checks.Error(
                    "cc_admin must come before django.contrib.admin in INSTALLED_APPS.",
                    hint="Move 'cc_admin' above 'django.contrib.admin' so its templates win.",
                    id="cc_admin.E001",
                )
            ]
    return []


def check_live(app_configs=None, **kwargs):
    from . import conf

    found = []
    push = conf.get("PUSH")
    if push.get("enabled") and not (push.get("vapid_public_key") and push.get("vapid_private_key")):
        found.append(
            checks.Warning(
                "PUSH is enabled but the VAPID keys are missing.",
                hint="Run python manage.py cc_admin_vapid and copy the keys into CC_ADMIN['PUSH'].",
                id="cc_admin.W001",
            )
        )
    if conf.get("LIVE").get("transport") == "websocket":
        if importlib.util.find_spec("channels") is None:
            found.append(
                checks.Warning(
                    "LIVE transport is websocket but channels is not installed.",
                    hint="pip install django-cc-admin[live] or use transport 'poll' or 'sse'.",
                    id="cc_admin.W002",
                )
            )
    return found
