###############
# Qiyas Sadıqov CC
###############

import base64

from django.core.management.base import BaseCommand, CommandError


def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


class Command(BaseCommand):
    help = "Make a VAPID key pair for push notifications."

    def handle(self, *args, **options):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import ec
        except ImportError as error:
            raise CommandError("Install the push extra first: pip install django-cc-admin[push]") from error
        key = ec.generate_private_key(ec.SECP256R1())
        private = b64(key.private_numbers().private_value.to_bytes(32, "big"))
        public = b64(key.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint))
        self.stdout.write("Add these to CC_ADMIN['PUSH'] and keep the private key out of version control:\n")
        self.stdout.write(f'"vapid_public_key": "{public}",')
        self.stdout.write(f'"vapid_private_key": "{private}",')
        self.stdout.write('"vapid_claims": {"sub": "mailto:you@example.com"},')
