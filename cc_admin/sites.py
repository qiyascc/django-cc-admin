###############
# Qiyas Sadıqov CC
###############

from django.contrib.admin import AdminSite
from django.urls import path

from . import views


def install():
    if getattr(AdminSite, "_cc_admin_installed", False):
        return
    get_urls = AdminSite.get_urls
    each_context = AdminSite.each_context

    def cc_get_urls(self):
        site = self

        def search(request):
            return views.search(request, site)

        return [path("cc/search/", self.admin_view(search), name="cc_search")] + get_urls(self)

    def cc_each_context(self, request):
        request._cc_admin_site = self
        return each_context(self, request)

    AdminSite.get_urls = cc_get_urls
    AdminSite.each_context = cc_each_context
    AdminSite._cc_admin_installed = True
