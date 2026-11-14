# Activity pages

`/admin/cc/activity/` shows what everyone did in the admin, in the style of a GitHub profile. It is built entirely from Django's own `LogEntry` table, the one behind the "History" button and "Recent actions". Nothing extra is recorded and no migration is needed.

```{image} ../screenshots/activity.jpg
:alt: The team activity page with totals, a year calendar, people and a monthly feed
```

## What is on the page

**Totals.** Changes in the period, the number of people, the models touched and the busiest day.

**A year long calendar.** One square per day, darker on busy days. Click a day to see exactly what happened: who changed which record, and which fields. The bar above the calendar splits the changes into added, changed and deleted.

**People.** Everyone who made changes, with their share, a small chart of the last twelve weeks, when they were last active and the model they touch most. Each person links to their own page.

**Contribution activity.** A monthly feed like GitHub's, with lines such as "Created 31 records in 4 models" and "Made 368 changes in 4 models", and a bar for each model.

**Year tabs.** "Last 12 months" and one tab per year that has changes.

Each staff user also has a personal page at `/admin/cc/activity/<user id>/` with the same calendar and feed for that person, their totals, and their current and longest streak of active days. "My activity" in the user menu and {kbd}`g` then {kbd}`a` lead there.

## Settings

```python
CC_ADMIN = {
    "ACTIVITY": {
        "enabled": True,
        "view": "staff",
        "others": "superuser",
        "team": True,
        "details": True,
        "weeks": 53,
        "exclude": ["auth.user"],
        "menu": True,
    },
}
```

`enabled`
: Turn the pages, the menu entry and the activity widgets off with `False`. `"ACTIVITY": False` does the same.

`view`
: Who may open the activity pages at all. Default `"staff"`.

`others`
: Who may see other people's activity. Everyone else only sees their own page. Default `"superuser"`.

`team`
: Show the team page at `/admin/cc/activity/`. With `False`, that address redirects to the user's own page. Default `True`.

`details`
: Show record names and change messages. With `False`, only counts are shown, which is useful when the records themselves are sensitive. Default `True`.

`weeks`
: The length of the calendar in weeks. Default 53.

`exclude`
: Models whose log entries are left out, as `"app_label.modelname"`.

`menu`
: Show "Activity" in the sidebar. Default `True`.

## Who may see what

`view` and `others` take the same values as every permission in django-cc-admin (see [Permissions](permissions.md)):

```python
"ACTIVITY": {
    "view": "staff",
    "others": "group:Managers",
}
```

Some common setups:

| Goal | Setting |
| --- | --- |
| Everybody on the team sees everybody | `"others": "staff"` |
| Only managers see the team | `"others": "group:Managers"` |
| People only ever see themselves | `"others": "none"` |
| Only people who may read the admin log see others | `"others": "perm:admin.view_logentry"` |

For finer rules, give a callable. For `others` it receives the request and, on a personal page, the person being looked at. On the team page there is no person, so give that argument a default:

```python
def can_see_person(request, person=None):
    if request.user.is_superuser:
        return True
    return person is not None and person.groups.filter(name="Support").exists() and request.user.groups.filter(name="Support leads").exists()


CC_ADMIN = {"ACTIVITY": {"others": can_see_person}}
```

People can always see their own page if they may see the activity pages at all. Links to records only show for models the viewer may open.

## Activity on the dashboard

Two dashboard widgets show the same data in a smaller form:

```python
"DASHBOARD": {
    "widgets": [
        {"type": "contributions", "title": "Your activity", "icon": "activity", "weeks": 30, "width": 8},
        {"type": "team", "title": "Team", "icon": "users", "days": 30, "width": 4},
    ],
},
```

See [Dashboard](dashboard.md#contributions) for their options.

## What is counted

Only changes made through the admin are counted, because only those are written to `LogEntry`. Changes made in a shell, an API or a background job do not show up, unless your code writes log entries itself with `LogEntry.objects.log_actions()` (or `log_action()` on older Django versions).

Large admin logs are fine: the pages count with database aggregates, and the calendar and people list read one year at a time. If the table grows very large, an index on `action_time` helps.
