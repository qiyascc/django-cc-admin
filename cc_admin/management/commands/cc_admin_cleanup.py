###############
# Qiyas Sadıqov CC
###############

from django.core.management.base import BaseCommand

from cc_admin import notify


class Command(BaseCommand):
    help = "Delete notifications older than NOTIFICATIONS['keep_days']."

    def handle(self, *args, **options):
        self.stdout.write(f"{notify.cleanup()} notifications deleted.")
