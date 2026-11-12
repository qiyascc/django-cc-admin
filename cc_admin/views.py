###############
# Qiyas Sadıqov CC
###############

from django.http import JsonResponse
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst

from . import conf, navigation
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
            queryset, _ = model_admin.get_search_results(request, queryset, query)
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
    return JsonResponse({"results": results[:60]})
