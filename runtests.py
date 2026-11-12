###############
# Qiyas Sadıqov CC
###############

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    sys.path[:0] = [str(ROOT), str(ROOT / "example")]
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    os.environ.setdefault("DATABASE_PATH", ":memory:")
    import django
    from django.conf import settings
    from django.test.utils import get_runner

    django.setup()
    runner = get_runner(settings)(verbosity=1)
    failures = runner.run_tests(sys.argv[1:] or ["tests"])
    sys.exit(bool(failures))
