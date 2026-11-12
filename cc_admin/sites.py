###############
# Qiyas Sadıqov CC
###############

import functools

from django.contrib.admin import AdminSite
from django.urls import path

from . import current, views


def install():
    if getattr(AdminSite, "_cc_admin_installed", False):
        return
    get_urls = AdminSite.get_urls
    each_context = AdminSite.each_context
    admin_view = AdminSite.admin_view

    def cc_admin_view(self, view, cacheable=False):
        inner = admin_view(self, view, cacheable)

        @functools.wraps(inner)
        def wrapped(request, *args, **kwargs):
            token = current.set(request)
            try:
                return inner(request, *args, **kwargs)
            finally:
                current.reset(token)

        return wrapped

    def cc_get_urls(self):
        site = self

        def search(request):
            return views.search(request, site)

        def activity_index(request):
            return views.activity_index(request, site)

        def activity_user(request, user_id):
            return views.activity_user(request, site, user_id)

        def bind(func):
            def view(request, *args, **kwargs):
                return func(request, site, *args, **kwargs)

            view.__name__ = func.__name__
            return view

        return [
            path("cc/search/", self.admin_view(search), name="cc_search"),
            path("cc/activity/", self.admin_view(activity_index), name="cc_activity"),
            path("cc/activity/<int:user_id>/", self.admin_view(activity_user), name="cc_activity_user"),
            path("cc/live/", self.admin_view(bind(views.live_poll)), name="cc_live"),
            path("cc/live/stream/", self.admin_view(bind(views.live_stream)), name="cc_live_stream"),
            path("cc/notifications/", self.admin_view(bind(views.notifications_page)), name="cc_notifications"),
            path("cc/notifications/read/", self.admin_view(bind(views.notifications_read)), name="cc_notifications_read"),
            path("cc/notifications/send/", self.admin_view(bind(views.broadcast)), name="cc_notifications_send"),
            path("cc/push/subscribe/", self.admin_view(bind(views.push_subscribe)), name="cc_push_subscribe"),
            path("cc/push/unsubscribe/", self.admin_view(bind(views.push_unsubscribe)), name="cc_push_unsubscribe"),
            path("cc/push/test/", self.admin_view(bind(views.push_test)), name="cc_push_test"),
            path("cc/sw.js", bind(views.service_worker), name="cc_service_worker"),
        ] + get_urls(self)

    def cc_each_context(self, request):
        request._cc_admin_site = self
        return each_context(self, request)

    AdminSite.admin_view = cc_admin_view
    AdminSite.get_urls = cc_get_urls
    AdminSite.each_context = cc_each_context
    AdminSite._cc_admin_installed = True
