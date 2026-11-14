# Colours, fonts and corners

Themes give you a starting point. This page shows how to change the colours, fonts and corners on top of them, for the whole site or for one theme at a time, how to build a theme of your own, and how to decide what each user may change in the appearance panel.

There are three levels, and each one wins over the one before it:

1. **The theme** sets every colour, font and size.
2. **Your settings** (`COLORS`, `FONTS`, `RADIUS`, `TOKENS`, and the per theme `THEMES` entries) change parts of it for everybody.
3. **The user's own choices** in the appearance panel (accent, font, text size, corners) change parts of it for that person only.

## Colours

`COLORS` takes friendly names. They apply on top of whatever theme is active.

```python
CC_ADMIN = {
    "COLORS": {
        "accent": "#e11d48",
        "sidebar": "#0f172a",
        "sidebar_text": "#cbd5e1",
        "dark": {
            "background": "#0b0b0f",
        },
    },
}
```

Keys at the top level apply in light mode and in dark mode. Keys under `"dark"` apply in dark mode only, and keys under `"light"` in light mode only.

| Key | What it changes |
| --- | --- |
| `accent` | Buttons, links, focus rings, active menu items, the first chart colour and the heatmap. Setting only `accent` also works out a hover shade and a readable text colour on top of it. |
| `accent_hover` | The hover shade of accent buttons. |
| `on_accent` | Text on accent coloured buttons. |
| `accent_text` | Links and accent coloured text. |
| `background`, `background_2` | The page background. |
| `surface`, `surface_2`, `surface_3` | Cards, menus and dialogs, from the lowest to the highest layer. |
| `border`, `border_strong` | Lines and dividers. |
| `text`, `text_muted`, `text_subtle` | Body text, secondary text and the faintest text. |
| `success`, `warning`, `danger`, `info` | Status colours used by badges, toasts, notes and charts. |
| `sidebar`, `sidebar_text`, `sidebar_active`, `sidebar_active_text` | The menu. |
| `topbar` | The bar at the top. |
| `input` | The background of form fields. |
| `heatmap` | The colour of activity and heatmap cells. |
| `chart` | A list of up to six colours for chart series. |

Any CSS colour works: hex, `rgb()`, `hsl()`, `oklch()` or `var(...)`. The automatic text colour for `accent` is only worked out for hex values, so with other formats set `on_accent` yourself.

```python
"COLORS": {
    "accent": "oklch(0.62 0.19 259)",
    "on_accent": "#ffffff",
    "chart": ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2"],
},
```

## Fonts

`FONTS` sets the font for body text, headings and code, and the base text size:

```python
CC_ADMIN = {
    "FONTS": {
        "body": "Manrope",
        "heading": "Fraunces",
        "mono": "JetBrains Mono",
        "size": 15,
    },
}
```

`size` is a number of pixels, or any CSS length as a string.

These fonts ship with the package and work by name, with no extra files:

| Sans serif | Serif | Monospace |
| --- | --- | --- |
| Geist, Manrope, DM Sans, Figtree, Plus Jakarta Sans, IBM Plex Sans, Nunito, Archivo, Space Grotesk | Source Serif 4, Fraunces | Geist Mono, JetBrains Mono, IBM Plex Mono, Space Mono |

Use `"system"` for the operating system's own font.

### Using another font

To use a font that is not bundled, load its stylesheet with `files` and use the family name:

```python
"FONTS": {
    "files": ["css/inter.css"],
    "body": "Inter",
},
```

`files` takes static paths or full URLs, so a Google Fonts stylesheet works too:

```python
"FONTS": {
    "files": ["https://fonts.googleapis.com/css2?family=Inter:wght@400..700&display=swap"],
    "body": "Inter",
},
```

A value with a comma is used as a full CSS font stack, as it is:

```python
"FONTS": {"body": '"Helvetica Neue", Arial, sans-serif'},
```

### Not loading the bundled fonts

The bundled fonts are loaded through one small stylesheet, and the browser only downloads the font files a page actually uses. If you only use your own fonts or the system font, you can skip that stylesheet:

```python
"FONTS": {"bundled": False, "body": "system"},
```

`"FONTS": False` also stops loading the bundled fonts. Each theme still asks for its own font family, and the browser falls back to the system font in the same stack.

## Corners

`RADIUS` sets how round buttons, cards and fields are:

```python
CC_ADMIN = {"RADIUS": "soft"}
```

| Value | Result |
| --- | --- |
| `"sharp"` | Square corners. |
| `"soft"` | 6 pixels. |
| `"round"` | 16 pixels. |
| `"default"` or `None` | Whatever the theme uses. |
| a number, like `10` | That many pixels. |
| a CSS length, like `"0.5rem"` | Used as it is. |

Small elements get a little less and large ones a little more, so the shapes stay in proportion.

## Low level tokens

Everything above is turned into CSS custom properties on the `<html>` element. `TOKENS` lets you set any of those properties directly. Write the name without the `--cc-` prefix:

```python
CC_ADMIN = {
    "TOKENS": {
        "side-w": "280px",
        "dark": {"shadow": "none"},
    },
}
```

`{"side-w": "280px"}` becomes `--cc-side-w: 280px`. As with `COLORS`, keys under `"dark"` and `"light"` apply to one mode only. The full list of properties is at the top of `cc_admin/static/cc_admin/css/cc.css`.

Values are checked before they reach the page. Names may only contain lowercase letters, digits and dashes, and values may not contain `;`, `{`, `}`, `<`, `>` or a backslash. Anything else is dropped.

## Settings for each theme

`THEMES` changes one built in theme without touching the others. Use the theme's key:

```python
CC_ADMIN = {
    "THEMES": {
        "aurora": {
            "label": "Company",
            "note": "Our colours",
            "colors": {"accent": "#0e8a8a", "sidebar": "#f2f7f7", "dark": {"accent": "#2dd4bf"}},
            "fonts": {"body": "Manrope", "heading": "Fraunces"},
            "radius": "soft",
            "layout": "topbar",
            "scheme": "dark",
            "density": "compact",
            "schemes": ["light", "dark"],
            "swatch": ["#f6fafa", "#ffffff", "#0e8a8a", "#13262b"],
            "tokens": {"side-w": "300px"},
        },
        "classic": {"enabled": False},
    },
}
```

Every key is optional:

| Key | Meaning |
| --- | --- |
| `label` | The name in the theme list. |
| `note` | The short line under the name. |
| `colors` | Like `COLORS`, for this theme only. |
| `fonts` | Like `FONTS` (`body`, `heading`, `mono`, `size`), for this theme only. |
| `radius` | Like `RADIUS`, for this theme only. |
| `tokens` | Like `TOKENS`, for this theme only. |
| `dark` | Raw tokens for this theme in dark mode only. |
| `layout` | `sidebar`, `topbar`, `rail` or `float`. |
| `scheme` | The mode this theme starts in until the user picks one: `auto`, `light` or `dark`. |
| `density` | The density this theme starts in: `compact`, `comfortable` or `spacious`. |
| `schemes` | The modes the theme supports, for example `["dark"]`. |
| `swatch` | Four colours for the little preview in the theme list: page, card, accent, text. |
| `enabled` | `False` removes the theme from the switcher. |

## A theme of your own

A key under `THEMES` that is not a built in theme creates a new one. It starts as a copy of the theme named in `extends` (Aurora if you leave it out) and applies your changes:

```python
CC_ADMIN = {
    "THEME": "acme",
    "THEMES": {
        "acme": {
            "extends": "midnight",
            "label": "Acme",
            "note": "Orange on navy",
            "colors": {"accent": "#f97316", "sidebar": "#0b1020"},
            "fonts": {"heading": "Space Grotesk"},
            "radius": 4,
            "swatch": ["#070b14", "#0d1424", "#f97316", "#e2e8f0"],
        },
    },
    "THEME_ORDER": ["acme", "aurora", "midnight"],
}
```

The new theme shows up in the appearance panel with its own preview, and `"THEME": "acme"` makes it the default. Without a `label` the key is turned into a title, so `"north_wind"` becomes "North Wind".

The example project has such a theme, called Northwind, built on Aurora with a teal accent:

```python
"THEMES": {
    "northwind": {
        "extends": "aurora",
        "label": "Northwind",
        "note": "Store colours on Aurora",
        "colors": {"accent": "#0e8a8a", "sidebar": "#f2f7f7"},
        "fonts": {"body": "Manrope"},
        "swatch": ["#f6fafa", "#ffffff", "#0e8a8a", "#13262b"],
    },
},
```

## What users may change

Besides theme, mode and density, the appearance panel lets each person pick an accent colour, a font, the text size and the corner style. The choice lives in their `cc_admin_prefs` cookie, so the page is drawn right on the first byte. `APPEARANCE` turns each control on or off and sets the choices:

```python
CC_ADMIN = {
    "APPEARANCE": {
        "accent": True,
        "accents": ["#5b5bd6", "#0e8a8a", "#e5484d"],
        "font": True,
        "fonts": ["Geist", "Manrope", "Source Serif 4", "system"],
        "font_size": True,
        "radius": True,
    },
}
```

| Key | Default | Meaning |
| --- | --- | --- |
| `accent` | `True` | Show the accent colour picker. |
| `accents` | nine colours | The colours offered as swatches. People can still pick any colour with the eyedropper. |
| `font` | `True` | Show the font menu. |
| `fonts` | twelve fonts | The fonts offered. Defaults to Geist, Manrope, DM Sans, Figtree, Plus Jakarta Sans, IBM Plex Sans, Nunito, Archivo, Space Grotesk, Source Serif 4, JetBrains Mono and System. |
| `font_size` | `True` | Show the text size control (13 to 17 pixels). |
| `radius` | `True` | Show the corner control (Sharp, Soft, Round). |

`"APPEARANCE": False` hides all four and leaves only theme, mode and density. `"THEME_SWITCHER": False` hides the whole panel, as described in [Themes](themes.md#one-theme-for-everybody).

A "Reset to theme" link at the bottom of the panel clears the user's accent, font, size and corners.

## Extra CSS and JavaScript

When settings are not enough, add your own files. They load after the package's own CSS and JavaScript, on every admin page:

```python
CC_ADMIN = {
    "STYLES": ["css/admin-extra.css"],
    "SCRIPTS": ["js/admin-extra.js"],
}
```

Both take static paths or full URLs. In your CSS you can use the same custom properties the themes use:

```css
html.cc .cc-card {
  box-shadow: none;
  border-width: 2px;
}

html.cc[data-skin="aurora"] .cc-badge {
  text-transform: uppercase;
}
```

The `<html>` element carries `data-skin` (the theme key), `data-theme` (the built in theme it is based on, the same as `data-skin` for built in themes), `data-scheme` (`auto`, `light` or `dark`), `data-density` and `data-layout`, so you can target any combination.
