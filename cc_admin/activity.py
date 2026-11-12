###############
# Qiyas Sadıqov CC
###############

import datetime
from collections import defaultdict

from django.conf import settings as dj_settings
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.admin.utils import quote
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Max, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from . import conf, navigation

VERBS = {ADDITION: "added", CHANGE: "changed", DELETION: "deleted"}
VERB_ICONS = {"added": "plus", "changed": "pencil", "deleted": "trash"}


def settings():
    return conf.get("ACTIVITY")


def enabled(request):
    data = settings()
    return bool(data.get("enabled")) and conf.rule(data.get("view"), request)


def can_see_others(request):
    return enabled(request) and conf.rule(settings().get("others"), request)


def can_see(request, target):
    if not enabled(request):
        return False
    if target is not None and target.pk == getattr(request.user, "pk", None):
        return True
    return conf.rule(settings().get("others"), request, target)


def site_name(request):
    site = getattr(request, "_cc_admin_site", None)
    return site.name if site else "admin"


def url(request, user=None):
    name = site_name(request)
    try:
        if user is None:
            return reverse(f"{name}:cc_activity")
        return reverse(f"{name}:cc_activity_user", args=[user.pk if hasattr(user, "pk") else user])
    except NoReverseMatch:
        return ""


def excluded_types():
    ids = []
    for label in settings().get("exclude") or []:
        try:
            app_label, model = label.lower().split(".")
            ids.append(ContentType.objects.get_by_natural_key(app_label, model).pk)
        except (ValueError, ContentType.DoesNotExist):
            continue
    return ids


def entries(user=None, start=None, end=None):
    queryset = LogEntry.objects.all()
    skip = excluded_types()
    if skip:
        queryset = queryset.exclude(content_type_id__in=skip)
    if user is not None:
        queryset = queryset.filter(user=user)
    if start is not None:
        queryset = queryset.filter(action_time__gte=_midnight(start))
    if end is not None:
        queryset = queryset.filter(action_time__lt=_midnight(end + datetime.timedelta(days=1)))
    return queryset


def _midnight(day):
    value = datetime.datetime.combine(day, datetime.time.min)
    if dj_settings.USE_TZ:
        return timezone.make_aware(value, timezone.get_current_timezone())
    return value


def day_counts(queryset):
    rows = queryset.annotate(day=TruncDate("action_time")).values("day").annotate(n=Count("id"))
    return {row["day"]: row["n"] for row in rows if row["day"]}


def thresholds(counts):
    values = sorted(v for v in counts.values() if v)
    if not values:
        return (1, 2, 3)
    pick = lambda q: values[min(len(values) - 1, int(len(values) * q))]
    return (pick(0.25), pick(0.5), pick(0.8))


def level(value, limits):
    if not value:
        return 0
    if value <= limits[0]:
        return 1
    if value <= limits[1]:
        return 2
    if value <= limits[2]:
        return 3
    return 4


def window(year=None, weeks=None):
    today = timezone.localdate()
    if year:
        start = datetime.date(year, 1, 1)
        end = min(datetime.date(year, 12, 31), today) if year == today.year else datetime.date(year, 12, 31)
        return start, end, datetime.date(year, 12, 31)
    weeks = int(weeks or settings().get("weeks") or 53)
    start = today - datetime.timedelta(days=today.weekday() + (weeks - 1) * 7)
    return start, today, today


def calendar(counts, start, end, last, selected=None):
    today = timezone.localdate()
    limits = thresholds(counts)
    first = start - datetime.timedelta(days=start.weekday())
    weeks = ((last - first).days // 7) + 1
    columns, months, last_month = [], [], None
    for w in range(weeks):
        cells = []
        for d in range(7):
            day = first + datetime.timedelta(days=w * 7 + d)
            value = counts.get(day, 0)
            cells.append(
                {
                    "date": day,
                    "iso": day.isoformat(),
                    "value": value,
                    "level": level(value, limits),
                    "hidden": day < start or day > last,
                    "future": day > today,
                    "selected": selected == day,
                }
            )
        month_day = next((c["date"] for c in cells if not c["hidden"] and c["date"].day <= 7), None)
        if month_day and month_day.month != last_month:
            if not months or w - months[-1][0] >= 3:
                months.append((w, date_format(month_day, "M")))
            last_month = month_day.month
        columns.append(cells)
    return {"weeks": columns, "months": months, "count": weeks, "total": sum(v for k, v in counts.items() if start <= k <= end)}


def streaks(counts, end):
    days = sorted(d for d, v in counts.items() if v)
    longest = run = 0
    previous = None
    for day in days:
        run = run + 1 if previous and (day - previous).days == 1 else 1
        longest = max(longest, run)
        previous = day
    current = 0
    cursor = end if counts.get(end) else end - datetime.timedelta(days=1)
    while counts.get(cursor):
        current += 1
        cursor -= datetime.timedelta(days=1)
    busiest = max(counts.items(), key=lambda item: item[1], default=(None, 0))
    return {"longest": longest, "current": current, "busiest": busiest[0], "busiest_count": busiest[1], "active_days": len(days)}


class Labels:
    def __init__(self, request):
        self.request = request
        self.cache = {}

    def model(self, content_type_id):
        if content_type_id in self.cache:
            return self.cache[content_type_id]
        try:
            ct = ContentType.objects.get_for_id(content_type_id)
        except ContentType.DoesNotExist:
            self.cache[content_type_id] = None
            return None
        model = ct.model_class()
        opts = model._meta if model else None
        user = self.request.user
        name = site_name(self.request)
        can_open = bool(opts) and (user.has_perm(f"{ct.app_label}.view_{ct.model}") or user.has_perm(f"{ct.app_label}.change_{ct.model}"))
        info = {
            "key": f"{ct.app_label}.{ct.model}",
            "label": capfirst(opts.verbose_name_plural) if opts else capfirst(ct.name),
            "single": capfirst(opts.verbose_name) if opts else capfirst(ct.name),
            "icon": navigation.model_icon(ct.app_label, opts.object_name if opts else ct.model),
            "app": ct.app_label,
            "model": ct.model,
            "can_open": can_open,
            "list_url": "",
        }
        if can_open:
            try:
                info["list_url"] = reverse(f"{name}:{ct.app_label}_{ct.model}_changelist")
            except NoReverseMatch:
                pass
        self.cache[content_type_id] = info
        return info

    def object_url(self, entry, model):
        if not model or not model["can_open"] or entry.action_flag == DELETION or not entry.object_id:
            return ""
        try:
            return reverse(f"{site_name(self.request)}:{model['app']}_{model['model']}_change", args=[quote(entry.object_id)])
        except NoReverseMatch:
            return ""


def sentence(verb, count, models):
    model_text = ngettext("%(m)s model", "%(m)s models", models) % {"m": models}
    if verb == "added":
        return _("Created %(records)s in %(models)s") % {"records": ngettext("%(n)s record", "%(n)s records", count) % {"n": count}, "models": model_text}
    if verb == "deleted":
        return _("Deleted %(records)s from %(models)s") % {"records": ngettext("%(n)s record", "%(n)s records", count) % {"n": count}, "models": model_text}
    return _("Made %(changes)s in %(models)s") % {"changes": ngettext("%(n)s change", "%(n)s changes", count) % {"n": count}, "models": model_text}


def summary(queryset, labels, by_month=True):
    group = TruncMonth("action_time") if by_month else TruncDate("action_time")
    rows = queryset.annotate(period=group).values("period", "action_flag", "content_type").annotate(n=Count("id"), objects=Count("object_id", distinct=True))
    periods = defaultdict(lambda: defaultdict(list))
    for row in rows:
        model = labels.model(row["content_type"])
        if model is None:
            continue
        verb = VERBS.get(row["action_flag"], "changed")
        periods[row["period"]][verb].append({**model, "count": row["n"], "objects": row["objects"]})
    result = []
    for period in sorted(periods, reverse=True):
        lines = []
        for verb in ("added", "changed", "deleted"):
            models = sorted(periods[period].get(verb, []), key=lambda m: -m["count"])
            if not models:
                continue
            total = sum(m["count"] for m in models)
            peak = models[0]["count"] or 1
            for m in models:
                m["share"] = round(m["count"] / peak * 100, 1)
            lines.append({"verb": verb, "icon": VERB_ICONS[verb], "count": total, "text": sentence(verb, total, len(models)), "models": models})
        day = period.date() if isinstance(period, datetime.datetime) else period
        result.append({"period": day, "lines": lines, "total": sum(line["count"] for line in lines)})
    return result


def day_feed(user, labels, day, details=True, group_by_user=False):
    items = entries(user=user, start=day, end=day).select_related("user").order_by("-action_time")
    groups = {}
    for entry in items[:500]:
        model = labels.model(entry.content_type_id)
        if model is None:
            continue
        verb = VERBS.get(entry.action_flag, "changed")
        key = entry.user_id if group_by_user else model["key"]
        if key not in groups:
            groups[key] = {
                "user": person(entry.user, labels.request) if group_by_user else None,
                "model": None if group_by_user else model,
                "items": [],
                "verbs": defaultdict(int),
                "models": set(),
            }
        group = groups[key]
        group["verbs"][verb] += 1
        group["models"].add(model["key"])
        group["items"].append(
            {
                "time": entry.action_time,
                "verb": verb,
                "icon": VERB_ICONS[verb],
                "model": model,
                "repr": entry.object_repr if details else "",
                "url": labels.object_url(entry, model) if details else "",
                "message": entry.get_change_message() if details and verb == "changed" else "",
            }
        )
    result = []
    for group in groups.values():
        parts = []
        for verb in ("added", "changed", "deleted"):
            if group["verbs"].get(verb):
                parts.append({"verb": verb, "count": group["verbs"][verb]})
        group["parts"] = parts
        group["total"] = sum(p["count"] for p in parts)
        group["model_count"] = len(group["models"])
        group["verbs"] = dict(group["verbs"])
        result.append(group)
    result.sort(key=lambda g: -g["total"])
    return result


def person(user, request=None):
    if user is None:
        return None
    full = user.get_full_name() if hasattr(user, "get_full_name") else ""
    return {
        "pk": user.pk,
        "name": full or user.get_username(),
        "username": user.get_username(),
        "email": getattr(user, "email", ""),
        "superuser": getattr(user, "is_superuser", False),
        "staff": getattr(user, "is_staff", False),
        "active": getattr(user, "is_active", True),
        "joined": getattr(user, "date_joined", None),
        "last_login": getattr(user, "last_login", None),
        "url": url(request, user) if request is not None and can_see(request, user) else "",
    }


def people(request, start, end, limit=None):
    queryset = entries(start=start, end=end)
    stats = {
        row["user"]: row
        for row in queryset.values("user").annotate(n=Count("id"), last=Max("action_time"), models=Count("content_type", distinct=True))
    }
    week_start = end - datetime.timedelta(days=end.weekday() + 11 * 7)
    weekly = defaultdict(lambda: [0] * 12)
    for row in entries(start=week_start, end=end).annotate(day=TruncDate("action_time")).values("user", "day").annotate(n=Count("id")):
        if row["day"] is None:
            continue
        index = min(11, max(0, (row["day"] - week_start).days // 7))
        weekly[row["user"]][index] += row["n"]
    top = {}
    for row in queryset.values("user", "content_type").annotate(n=Count("id")).order_by("user", "-n"):
        top.setdefault(row["user"], row["content_type"])
    labels = Labels(request)
    User = get_user_model()
    users = User.objects.filter(Q(is_staff=True, is_active=True) | Q(pk__in=list(stats))).order_by("pk")
    result = []
    for user in users:
        row = stats.get(user.pk, {})
        data = person(user, request)
        week = weekly.get(user.pk, [0] * 12)
        peak = max(week) or 1
        data.update(
            {
                "count": row.get("n", 0),
                "last": row.get("last"),
                "models": row.get("models", 0),
                "weeks": [{"value": v, "share": round(v / peak * 100)} for v in week],
                "top": labels.model(top[user.pk]) if user.pk in top else None,
            }
        )
        result.append(data)
    result.sort(key=lambda p: (-p["count"], p["name"].lower()))
    total = sum(p["count"] for p in result) or 1
    for p in result:
        p["share"] = round(p["count"] / total * 100, 1)
    return result[:limit] if limit else result


def years(user=None):
    queryset = entries(user=user)
    found = sorted({d.year for d in queryset.dates("action_time", "year")}, reverse=True)
    this = timezone.localdate().year
    if this not in found:
        found.insert(0, this)
    return found


def parse_day(value):
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def parse_year(value):
    try:
        year = int(value)
    except (TypeError, ValueError):
        return None
    return year if 1990 <= year <= 2200 else None


def overview(request, user=None, year=None, day=None):
    start, end, last = window(year)
    scope = entries(user=user, start=start, end=end)
    counts = day_counts(scope)
    labels = Labels(request)
    details = bool(settings().get("details"))
    data = {
        "start": start,
        "end": end,
        "year": year,
        "calendar": calendar(counts, start, end, last, day),
        "stats": streaks(counts, end),
        "total": sum(counts.values()),
        "models_touched": scope.values("content_type").distinct().count(),
        "split": {VERBS[row["action_flag"]]: row["n"] for row in scope.values("action_flag").annotate(n=Count("id")) if row["action_flag"] in VERBS},
        "day": day,
        "details": details,
    }
    if day:
        data["feed"] = day_feed(user, labels, day, details, group_by_user=user is None)
        data["day_total"] = sum(g["total"] for g in data["feed"])
    else:
        data["months"] = summary(scope, labels)
    return data


def widget(request, scope="me", weeks=26):
    if not enabled(request):
        return None
    user = request.user if scope != "all" or not can_see_others(request) else None
    start, end, last = window(weeks=weeks)
    counts = day_counts(entries(user=user, start=start, end=end))
    data = calendar(counts, start, end, last)
    data["stats"] = streaks(counts, end)
    data["link"] = url(request, user)
    data["user"] = user
    return data


def label_for(verb):
    return {"added": _("added"), "changed": _("changed"), "deleted": _("deleted")}.get(verb, verb)
