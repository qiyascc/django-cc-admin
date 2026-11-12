###############
# Qiyas Sadıqov CC
###############

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from . import activity, conf, navigation
from .admin import plain


def search(request, site):
    settings = conf.get("COMMAND_PALETTE")
    query = request.GET.get("q", "").strip()
    if not settings.get("enabled") or not settings.get("search_models") or len(query) < settings.get("min_length", 2):
        return JsonResponse({"results": []})
    limit = max(1, min(int(settings.get("limit", 5)), 25))
    request._cc_admin_site = site
    results = []
    for model, model_admin in site._registry.items():
        if not model_admin.get_search_fields(request) or not model_admin.has_view_permission(request):
            continue
        opts = model._meta
        try:
            queryset = model_admin.get_queryset(request)
            queryset, _unused = model_admin.get_search_results(request, queryset, query)
            objects = list(queryset[:limit])
        except Exception:
            continue
        for obj in objects:
            try:
                url = reverse(f"{site.name}:{opts.app_label}_{opts.model_name}_change", args=[obj.pk], current_app=site.name)
            except NoReverseMatch:
                continue
            results.append(
                {
                    "title": plain(str(obj))[:120],
                    "model": capfirst(opts.verbose_name),
                    "icon": navigation.model_icon(opts.app_label, opts.object_name),
                    "url": url,
                }
            )
    if settings.get("search_callback"):
        extra = conf.call(settings["search_callback"], request, query) or []
        results = [
            {"title": str(r.get("title", "")), "model": str(r.get("subtitle", r.get("model", ""))), "icon": r.get("icon", "arrow-right"), "url": conf.link(r.get("link") or r.get("url"), request)}
            for r in extra
        ] + results
    return JsonResponse({"results": results[:60]})


def _activity_context(request, site, user=None):
    year = activity.parse_year(request.GET.get("year"))
    day = activity.parse_day(request.GET.get("day"))
    data = activity.overview(request, user, year, day)
    query = f"?year={year}&" if year else "?"
    return {
        **site.each_context(request),
        "activity": data,
        "years": activity.years(user),
        "base_query": query,
        "team_url": activity.url(request) if activity.can_see_others(request) and activity.settings().get("team") else "",
        "is_popup": False,
    }


def activity_index(request, site):
    request._cc_admin_site = site
    if not activity.enabled(request):
        raise PermissionDenied
    if not activity.settings().get("team") or not activity.can_see_others(request):
        return HttpResponseRedirect(activity.url(request, request.user))
    context = _activity_context(request, site)
    data = context["activity"]
    if request.GET.get("partial"):
        return TemplateResponse(request, "cc_admin/activity/feed.html", context)
    context.update(
        {
            "title": _("Activity"),
            "people": activity.people(request, data["start"], data["end"]),
            "subject": None,
        }
    )
    return TemplateResponse(request, "cc_admin/activity/team.html", context)


def activity_user(request, site, user_id):
    request._cc_admin_site = site
    target = get_object_or_404(get_user_model(), pk=user_id)
    if not activity.can_see(request, target):
        raise PermissionDenied
    context = _activity_context(request, site, target)
    if request.GET.get("partial"):
        return TemplateResponse(request, "cc_admin/activity/feed.html", context)
    subject = activity.person(target, request)
    context.update({"title": subject["name"], "subject": subject, "is_self": target.pk == request.user.pk})
    return TemplateResponse(request, "cc_admin/activity/user.html", context)


class AdminPageView(TemplateView):
    model_admin = None
    admin_site = None
    title = ""
    subtitle = ""
    icon = None
    permission_required = ()
    template_name = "cc_admin/page.html"

    def get_site(self):
        if self.model_admin is not None:
            return self.model_admin.admin_site
        if self.admin_site is not None:
            return self.admin_site
        from django.contrib import admin

        return admin.site

    def has_permission(self, request):
        perms = self.permission_required
        if isinstance(perms, str):
            perms = (perms,)
        if callable(perms):
            return bool(perms(request))
        return request.user.has_perms(perms)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        site = self.get_site()
        context = {**site.each_context(self.request), **super().get_context_data(**kwargs)}
        context.setdefault("title", self.title)
        context.setdefault("subtitle", self.subtitle)
        if self.model_admin is not None:
            context.setdefault("opts", self.model_admin.opts)
        context["cc_page"] = self
        return context
