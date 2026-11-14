# Python API

These are the classes and functions meant for your code. Everything else in the package is internal and may change between versions. The guides explain each of them with examples; this page gives the exact signatures.

## cc_admin.admin

`ModelAdmin` is Django's `ModelAdmin` plus `ModelAdminMixin`. Use the mixin when combining with another package's base class. The options it adds are listed in [ModelAdmin extras](../guides/model-admin.md#list-options).

```{eval-rst}
.. autoclass:: cc_admin.admin.ModelAdmin
   :no-members:

.. autoclass:: cc_admin.admin.ModelAdminMixin
   :no-members:

   .. automethod:: cc_export_rows
   .. automethod:: cc_export_response
```

`cc_export_rows(request, queryset)` yields the header row and then one list of strings per object. `cc_export_response(request, queryset, fmt)` turns those rows into a CSV or JSON download. Override either to change [what is exported](../guides/export.md#changing-what-is-exported).

```{eval-rst}
.. autoclass:: cc_admin.admin.TabularInline
   :no-members:

.. autoclass:: cc_admin.admin.StackedInline
   :no-members:

.. autoclass:: cc_admin.admin.InlineMixin
   :no-members:
```

The inline options are `tab`, `collapsible`, `hide_title` and `ordering_field`. See [Inlines](../guides/model-admin.md#inlines).

## cc_admin.decorators

```{eval-rst}
.. autofunction:: cc_admin.decorators.display

.. autofunction:: cc_admin.decorators.action
```

`display` returns a function decorated with Django's `admin.display`, drawn as a badge, header, thumbnail, progress bar, tag list or copyable value. `action` returns a function decorated with Django's `admin.action` and carries the icon, variant, confirmation and URL path for the button. See [Richer list columns](../guides/model-admin.md#richer-list-columns-with-display) and [Actions](../guides/actions.md).

## cc_admin.filters

All filters are used as `(field, FilterClass)` in `list_filter`, except `TextFilter` and `DropdownFilter`, which you subclass. See [Filters](../guides/filters.md).

```{eval-rst}
.. autoclass:: cc_admin.filters.FieldTextFilter
   :no-members:

.. autoclass:: cc_admin.filters.FieldExactFilter
   :no-members:

.. autoclass:: cc_admin.filters.TextFilter
   :no-members:

.. autoclass:: cc_admin.filters.RangeNumericFilter
   :no-members:

.. autoclass:: cc_admin.filters.SliderNumericFilter
   :no-members:

.. autoclass:: cc_admin.filters.SingleNumericFilter
   :no-members:

.. autoclass:: cc_admin.filters.RangeDateFilter
   :no-members:

.. autoclass:: cc_admin.filters.RangeDateTimeFilter
   :no-members:

.. autoclass:: cc_admin.filters.ChoicesCheckboxFilter
   :no-members:

.. autoclass:: cc_admin.filters.RelatedCheckboxFilter
   :no-members:

.. autoclass:: cc_admin.filters.AllValuesCheckboxFilter
   :no-members:

.. autoclass:: cc_admin.filters.DropdownFilter
   :no-members:

.. autoclass:: cc_admin.filters.ChoicesDropdownFilter
   :no-members:

.. autoclass:: cc_admin.filters.RelatedDropdownFilter
   :no-members:

.. autoclass:: cc_admin.filters.AllValuesDropdownFilter
   :no-members:

.. autoclass:: cc_admin.filters.BooleanRadioFilter
   :no-members:
```

## cc_admin.sections

```{eval-rst}
.. autoclass:: cc_admin.sections.Section
   :members: get_title, get_context_data, render

.. autoclass:: cc_admin.sections.TableSection
   :members: get_queryset

.. autoclass:: cc_admin.sections.TemplateSection
   :no-members:
```

A section is created with `(model_admin, request, obj)` and has those three as attributes. `TableSection` takes `related_name`, `fields`, `limit`, `height` and `empty_text`. See [Expandable rows and sections](../guides/sections.md).

## cc_admin.widgets

```{eval-rst}
.. autoclass:: cc_admin.widgets.SwitchWidget
   :no-members:

.. autoclass:: cc_admin.widgets.SegmentedWidget
   :no-members:

.. autoclass:: cc_admin.widgets.ColorWidget
   :no-members:

.. autoclass:: cc_admin.widgets.RichTextWidget
   :no-members:

.. autoclass:: cc_admin.widgets.CodeWidget
   :no-members:

.. autoclass:: cc_admin.widgets.JSONWidget
   :no-members:

.. autoclass:: cc_admin.widgets.ImageWidget
   :no-members:

.. autoclass:: cc_admin.widgets.CounterTextarea
   :no-members:
```

See [Form widgets](../guides/widgets.md).

## cc_admin.views

```{eval-rst}
.. autoclass:: cc_admin.views.AdminPageView
   :members: get_site, has_permission, get_context_data
```

See [Custom pages](../guides/custom-pages.md).

## cc_admin.notify

```{eval-rst}
.. autofunction:: cc_admin.notify.notify

.. autofunction:: cc_admin.notify.recipients

.. autofunction:: cc_admin.notify.mark_read

.. autofunction:: cc_admin.notify.send_push

.. autofunction:: cc_admin.notify.cleanup
```

`notify()` creates one `Notification` per recipient and returns them. `recipients(to)` returns the queryset of active users that `to` stands for, which is handy for checking a rule. `mark_read(user, ids=None)` marks notifications read and returns how many changed. `send_push(user_ids, note)` sends a push for an existing notification and waits until it is done; it returns the number of messages sent. `cleanup()` deletes notifications older than `keep_days` and returns how many. See [Notifications](../guides/notifications.md).

## cc_admin.models

```{eval-rst}
.. autoclass:: cc_admin.models.Notification
   :no-members:

   .. autoattribute:: is_read
   .. automethod:: as_json

.. autoclass:: cc_admin.models.PushSubscription
   :no-members:
```

| `Notification` field | Type |
| --- | --- |
| `recipient` | Foreign key to the user model. `user.cc_notifications` is the reverse relation. |
| `actor` | Foreign key to the user model, nullable. |
| `title` | `CharField(200)` |
| `body` | `TextField` |
| `link` | `CharField(500)` |
| `level` | `CharField(16)`, one of `info`, `success`, `warning`, `danger`, `accent`, `neutral`. |
| `icon` | `CharField(64)` |
| `sound` | `CharField(32)` |
| `key` | `CharField(120)` |
| `data` | `JSONField` |
| `created_at` | `DateTimeField`, indexed. |
| `read_at` | `DateTimeField`, nullable. |

`PushSubscription` has `user` (reverse relation `user.cc_push_subscriptions`), `endpoint`, `p256dh`, `auth`, `user_agent`, `created_at` and `last_used_at`.

## cc_admin.icons

```{eval-rst}
.. autofunction:: cc_admin.icons.icon

.. autofunction:: cc_admin.icons.exists

.. autofunction:: cc_admin.icons.symbols
```

`icon(name, cls="", label=None)` returns safe SVG markup for one icon, the same as the `{% icon %}` tag. `exists(name)` tells whether a name is in the bundled set, and `symbols()` returns all of them as a dict keyed by name.

## cc_admin.routing

`websocket_urlpatterns` is the list of WebSocket routes for Channels. See [Live updates](../guides/live-updates.md#websockets).

## cc_admin

`cc_admin.__version__` is the installed version as a string.
