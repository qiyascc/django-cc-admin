# Keyboard shortcuts

Most things in the admin can be done from the keyboard. Press {kbd}`?` on any page to see every shortcut that applies there.

```{image} ../screenshots/shortcuts.jpg
:alt: The keyboard shortcuts dialog with Anywhere, Lists, Forms and your own shortcuts
```

## The defaults

{kbd}`Ctrl` means {kbd}`⌘` on a Mac. "g then d" means press {kbd}`g`, let go, then press {kbd}`d`.

**Anywhere**

| Keys | Action | Name |
| --- | --- | --- |
| {kbd}`Ctrl+K` | Command palette | `palette` |
| {kbd}`?` | Show keyboard shortcuts | `help` |
| {kbd}`/` | Focus search | `search` |
| {kbd}`g` then {kbd}`d` | Go to dashboard | `dashboard` |
| {kbd}`g` then {kbd}`a` | Go to activity | `activity` |
| {kbd}`g` then {kbd}`s` | Go to site | `site` |
| {kbd}`t` | Appearance panel | `theme` |
| {kbd}`[` | Collapse menu | `menu` |

**Lists**

| Keys | Action | Name |
| --- | --- | --- |
| {kbd}`j` | Next row | `next_row` |
| {kbd}`k` | Previous row | `prev_row` |
| {kbd}`x` | Select row | `select_row` |
| {kbd}`Shift+X` | Select all rows | `select_all` |
| {kbd}`o` or {kbd}`Enter` | Open row | `open_row` |
| {kbd}`Shift+O` | Open row in a new tab | `open_row_tab` |
| {kbd}`Space` | Expand row | `expand_row` |
| {kbd}`n` | Add new | `add` |
| {kbd}`f` | Open filters | `filters` |
| {kbd}`c` | Choose columns | `columns` |
| {kbd}`e` | Export current view | `export` |
| {kbd}`←` | Previous page | `prev_page` |
| {kbd}`→` | Next page | `next_page` |

**Forms**

| Keys | Action | Name |
| --- | --- | --- |
| {kbd}`Ctrl+Enter` | Save | `save` |
| {kbd}`Ctrl+S` | Save and keep editing | `save_continue` |
| {kbd}`Ctrl+Shift+Enter` | Save and add another | `save_add` |
| {kbd}`Alt+→` | Next tab | `next_tab` |
| {kbd}`Alt+←` | Previous tab | `prev_tab` |
| {kbd}`g` then {kbd}`h` | Open history | `history` |
| {kbd}`g` then {kbd}`l` | Back to the list | `back` |
| none | Delete this record | `delete` |

`delete` has no keys by default, so nobody deletes a record by accident. Give it keys in settings if you want it.

Single letter shortcuts do nothing while you type in a field, so {kbd}`j` in a text box is just a "j".

## Changing the keys

```python
CC_ADMIN = {
    "SHORTCUTS": {
        "enabled": True,
        "user_editable": True,
        "keys": {
            "filters": "shift+f",
            "open_row": ["o", "enter"],
            "theme": None,
            "delete": "mod+shift+backspace",
        },
    },
}
```

`keys` maps an action name from the tables above to new keys:

- write a combination with `+`: `"shift+f"`, `"mod+k"`, `"alt+arrowright"`,
- write a sequence with a space: `"g o"` means {kbd}`g` then {kbd}`o`, up to three steps,
- give a list for several alternatives: `["o", "enter"]`,
- give `None` to turn an action off.

`mod` is {kbd}`Ctrl` on Windows and Linux and {kbd}`⌘` on a Mac. `ctrl`, `cmd`, `command` and `meta` all mean the same as `mod`. Other names that work: `alt` (or `option`), `shift`, `enter` (or `return`), `escape` (or `esc`), `space`, `backspace`, `delete`, `tab`, `arrowleft`, `arrowright`, `arrowup`, `arrowdown` (or `left`, `right`, `up`, `down`), and any single character. The order of the modifiers does not matter.

## Your own shortcuts

`custom` adds new shortcuts that open a link or click an element on the page:

```python
CC_ADMIN = {
    "SHORTCUTS": {
        "custom": [
            {"keys": "g o", "title": "Open orders", "link": "admin:shop_order_changelist"},
            {"keys": "g r", "title": "Reports", "link": "admin:shop_order_reports", "permission": "perm:shop.view_order"},
            {"keys": "g w", "title": "Warehouse", "link": "https://warehouse.example.com/", "new_tab": True},
            {"keys": "mod+shift+p", "title": "Print", "click": "#print-button"},
        ],
    },
}
```

| Key | Meaning |
| --- | --- |
| `keys` | The keys, written as above. |
| `title` | The description in the help dialog. |
| `link` | A URL name, path or full URL to open. |
| `new_tab` | Open the link in a new tab. |
| `click` | A CSS selector. The first matching element on the page is clicked. |
| `permission` | Who gets the shortcut. |
| `scope` | The heading it is listed under in the help dialog. Defaults to "Your shortcuts". |
| `id` | A stable name, so that a user's own rebinding survives when you reorder the list. |

Custom shortcuts may also be callables that take the request.

## Letting people rebind keys

With `user_editable` on (the default), people can click any shortcut in the {kbd}`?` dialog and press new keys. Their choice is kept in their browser and wins over the settings. If the new keys were used by another action, that action loses them. Once something is changed, a "Reset all" button in the dialog brings back your defaults.

Set `user_editable` to `False` to keep the keys fixed. `"SHORTCUTS": False` turns all shortcuts off, and the help dialog with them.
