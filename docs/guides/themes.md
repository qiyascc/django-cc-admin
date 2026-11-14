# Themes

django-cc-admin ships fifteen themes. They are more than colour swaps: each one has its own layout, type and shape, and most come in a light and a dark version. You choose the default for the site. Every user can then pick their own from the appearance panel, unless you turn the switcher off.

## The fifteen themes

| Key | Name | Layout | Modes | Character |
| --- | --- | --- | --- | --- |
| `aurora` | Aurora | sidebar | light, dark | Clean indigo. The default. |
| `midnight` | Midnight | sidebar | dark | Deep navy with a cyan edge. |
| `paper` | Paper | top bar | light, dark | Editorial serif headings on warm paper. |
| `terminal` | Terminal | icon rail | dark | Green phosphor, monospace everywhere. |
| `nord` | Nord | sidebar | light, dark | Arctic blues and frost, the Nord palette. |
| `brutal` | Brutal | top bar | light | Thick lines and hard shadows. |
| `glass` | Glass | floating | dark, light | Frosted panels over a soft glow. |
| `slate` | Slate | sidebar | light, dark | Dense enterprise grey, built for long tables. |
| `sunset` | Sunset | floating | light, dark | Warm coral and amber. |
| `forest` | Forest | sidebar | light, dark | Moss, bark and Fraunces titles. |
| `mono` | Mono | top bar | light, dark | Black and white, nothing else. |
| `rose` | Rose | floating | light, dark | Soft pink, round corners, pill buttons. |
| `ocean` | Ocean | icon rail | light, dark | Teal depths. |
| `classic` | Classic | sidebar | light | A desktop from 1995. |
| `cc` | CC | sidebar | dark, light | Ink and ice blue, the look of theqiyas.cc. |

The four layouts are:

`sidebar`
: A full menu on the left with group titles, icons and badges.

`topbar`
: The menu moves into a bar across the top. Good for wide tables.

`rail`
: A narrow column of icons on the left. Hovering shows the names.

`float`
: The menu floats as a rounded panel with space around it.

## Gallery

Each picture shows the dashboard, the order list and a product form of the example shop.

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Aurora
```{image} ../screenshots/aurora-light.jpg
:alt: Aurora theme
```
:::

:::{grid-item-card} Midnight
```{image} ../screenshots/midnight-dark.jpg
:alt: Midnight theme
```
:::

:::{grid-item-card} Paper
```{image} ../screenshots/paper-light.jpg
:alt: Paper theme
```
:::

:::{grid-item-card} Terminal
```{image} ../screenshots/terminal-dark.jpg
:alt: Terminal theme
```
:::

:::{grid-item-card} Nord
```{image} ../screenshots/nord-light.jpg
:alt: Nord theme
```
:::

:::{grid-item-card} Brutal
```{image} ../screenshots/brutal-light.jpg
:alt: Brutal theme
```
:::

:::{grid-item-card} Glass
```{image} ../screenshots/glass-dark.jpg
:alt: Glass theme
```
:::

:::{grid-item-card} Slate
```{image} ../screenshots/slate-light.jpg
:alt: Slate theme
```
:::

:::{grid-item-card} Sunset
```{image} ../screenshots/sunset-light.jpg
:alt: Sunset theme
```
:::

:::{grid-item-card} Forest
```{image} ../screenshots/forest-light.jpg
:alt: Forest theme
```
:::

:::{grid-item-card} Mono
```{image} ../screenshots/mono-light.jpg
:alt: Mono theme
```
:::

:::{grid-item-card} Rose
```{image} ../screenshots/rose-light.jpg
:alt: Rose theme
```
:::

:::{grid-item-card} Ocean
```{image} ../screenshots/ocean-light.jpg
:alt: Ocean theme
```
:::

:::{grid-item-card} Classic
```{image} ../screenshots/classic-light.jpg
:alt: Classic theme
```
:::

:::{grid-item-card} CC
```{image} ../screenshots/cc-dark.jpg
:alt: CC theme
```
:::
::::

## Choosing the default

```python
CC_ADMIN = {
    "THEME": "forest",
    "COLOR_SCHEME": "auto",
    "DENSITY": "comfortable",
}
```

`THEME`
: The key of the theme people get until they choose one. Defaults to `"aurora"`. An unknown key falls back to Aurora.

`COLOR_SCHEME`
: `"auto"` follows the operating system, `"light"` and `"dark"` force one. Defaults to `"auto"`. A theme that only has one mode, such as Midnight or Brutal, always uses that mode.

`DENSITY`
: How much space rows and cards get. `"compact"`, `"comfortable"` or `"spacious"`. The panel calls them Compact, Default and Roomy. Defaults to `"comfortable"`.

These three are plain values, read once when the settings load. Unlike texts and links, they do not accept a callable. A user's own choice in the appearance panel always wins over them.

A common trick during development is to read the theme from the environment, so you can try them without editing settings:

```python
import os

CC_ADMIN = {
    "THEME": os.environ.get("CC_THEME", "aurora"),
}
```

```bash
CC_THEME=terminal python manage.py runserver
```

## The appearance panel

Every user can open the appearance panel in three ways: click the theme name at the bottom of the menu, open the user menu in the top right, or press {kbd}`t` anywhere.

```{image} ../screenshots/appearance-panel.jpg
:alt: The appearance panel with mode, density, accent, font, text size, corners and the theme list
```

The panel has the mode (Auto, Light, Dark), the density, an accent colour, a font, the text size, the corner style and the list of themes with a small preview of each. The choice is saved in a cookie called `cc_admin_prefs`. Because the server reads that cookie, the page is drawn in the right theme from the first byte, with no flash of the default theme while JavaScript loads.

What the panel offers can be limited with the `APPEARANCE` setting, described in [Colours, fonts and corners](appearance.md).

## One theme for everybody

To lock the look, turn the switcher off:

```python
CC_ADMIN = {
    "THEME": "slate",
    "COLOR_SCHEME": "light",
    "THEME_SWITCHER": False,
}
```

With `THEME_SWITCHER` set to `False`, the panel disappears, the {kbd}`t` shortcut does nothing, and any `cc_admin_prefs` cookie a user already has is ignored. Everyone sees the theme, mode and density you set.

## Forcing a layout

`LAYOUT` overrides the layout of every theme:

```python
CC_ADMIN = {
    "LAYOUT": "topbar",
}
```

The value is one of `"sidebar"`, `"topbar"`, `"rail"` or `"float"`. Leave it at `None` (the default) to let each theme use its own layout. To change the layout of only one theme, use the `layout` key under `THEMES`, shown in [Settings for each theme](appearance.md#settings-for-each-theme).

## Hiding and ordering themes

Fifteen choices can be too many. Remove the ones you do not want and set the order of the rest:

```python
CC_ADMIN = {
    "THEMES": {
        "classic": {"enabled": False},
        "brutal": {"enabled": False},
        "terminal": {"enabled": False},
    },
    "THEME_ORDER": ["aurora", "slate", "nord", "midnight"],
}
```

Themes listed in `THEME_ORDER` come first in that order. Themes you did not list follow in their usual order.

## Your own theme

You can add a theme of your own on top of any built in one, with your colours, fonts and corners. That is covered in [Colours, fonts and corners](appearance.md#a-theme-of-your-own).

## Fonts and icons are local

All fonts and icons ship with the package and are served from your own static files. Nothing is loaded from Google Fonts or a CDN, so the admin works on an intranet and does not leak visits to third parties. The bundled fonts are listed in [Colours, fonts and corners](appearance.md#fonts).
