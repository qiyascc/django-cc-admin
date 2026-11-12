###############
# Qiyas Sadıqov CC
###############

import contextvars

_request = contextvars.ContextVar("cc_admin_request", default=None)


def request():
    return _request.get()


def user():
    current = _request.get()
    found = getattr(current, "user", None)
    return found if found is not None and found.is_authenticated else None


def set(value):
    return _request.set(value)


def reset(token):
    _request.reset(token)
