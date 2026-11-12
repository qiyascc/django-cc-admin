###############
# Qiyas Sadıqov CC
###############

from django.apps import AppConfig
from django.conf import settings
from django.core import checks


class CCAdminConfig(AppConfig):
    name = "cc_admin"
    label = "cc_admin"
    verbose_name = "CC Admin"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from . import sites

        sites.install()
        checks.register(check_order, checks.Tags.admin)


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
