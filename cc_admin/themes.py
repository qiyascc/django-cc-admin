###############
# Qiyas Sadıqov CC
###############

import json
import re
from urllib.parse import unquote
from dataclasses import asdict, dataclass, field

from . import conf

LAYOUTS = ("sidebar", "topbar", "rail", "float")
SCHEMES = ("auto", "light", "dark")
DENSITIES = ("compact", "comfortable", "spacious")


@dataclass(frozen=True)
class Theme:
    key: str
    label: str
    note: str
    layout: str = "sidebar"
    schemes: tuple = ("light", "dark")
    swatch: tuple = ("#ffffff", "#f4f4f5", "#4f46e5", "#18181b")
    extends: str = ""
    tokens: dict = field(default_factory=dict)
    dark: dict = field(default_factory=dict)
    default_scheme: str = ""
    density: str = ""

    @property
    def css_key(self):
        return self.extends or self.key

    def scheme_for(self, preference):
        if preference in self.schemes:
            return preference
        if len(self.schemes) == 1:
            return self.schemes[0]
        return "auto"

    def as_json(self):
        data = asdict(self)
        data["css_key"] = self.css_key
        return data


BUILTIN = [
    Theme("aurora", "Aurora", "Clean indigo, the default", "sidebar", ("light", "dark"), ("#fbfbfd", "#ffffff", "#5b5bd6", "#17171c")),
    Theme("midnight", "Midnight", "Deep navy with a cyan edge", "sidebar", ("dark",), ("#070b14", "#0d1424", "#22d3ee", "#e2e8f0")),
    Theme("paper", "Paper", "Editorial serif on warm paper", "topbar", ("light", "dark"), ("#f6f1e7", "#fffdf8", "#b4442c", "#2b2620")),
    Theme("terminal", "Terminal", "Green phosphor, all monospace", "rail", ("dark",), ("#050805", "#0a100a", "#4ade80", "#c8f7c5")),
    Theme("nord", "Nord", "Arctic blues and frost", "sidebar", ("light", "dark"), ("#eceff4", "#ffffff", "#5e81ac", "#2e3440")),
    Theme("brutal", "Brutal", "Thick lines, hard shadows", "topbar", ("light",), ("#fff6d6", "#ffffff", "#ff5c35", "#000000")),
    Theme("glass", "Glass", "Frosted panels over a soft glow", "float", ("dark", "light"), ("#0b0820", "#1a1440", "#a78bfa", "#f5f3ff")),
    Theme("slate", "Slate", "Dense enterprise grey", "sidebar", ("light", "dark"), ("#f1f3f5", "#ffffff", "#2563eb", "#111827")),
    Theme("sunset", "Sunset", "Warm coral and amber", "float", ("light", "dark"), ("#fff7f2", "#ffffff", "#f0573a", "#2a1712")),
    Theme("forest", "Forest", "Moss, bark and serif titles", "sidebar", ("light", "dark"), ("#f3f1ea", "#fbfaf6", "#2f6b4f", "#1f2a22")),
    Theme("mono", "Mono", "Black, white, nothing else", "topbar", ("light", "dark"), ("#ffffff", "#ffffff", "#000000", "#000000")),
    Theme("rose", "Rose", "Soft pink, round corners", "float", ("light", "dark"), ("#fdf2f6", "#ffffff", "#db2777", "#3b0a22")),
    Theme("ocean", "Ocean", "Teal depths, icon rail", "rail", ("light", "dark"), ("#f0f7f8", "#ffffff", "#0e8a8a", "#0b2a33")),
    Theme("classic", "Classic", "A desktop from 1995", "sidebar", ("light",), ("#008080", "#c0c0c0", "#000080", "#000000")),
    Theme("cc", "CC", "Ink and ice blue, the theqiyas.cc look", "sidebar", ("dark", "light"), ("#0c1014", "#12181e", "#8fb4cc", "#edf1f3")),
]


def _spec_tokens(spec):
    colors = spec.get("colors") or {}
    light = {
        **color_tokens({k: v for k, v in colors.items() if k not in ("light", "dark")}),
        **color_tokens(colors.get("light", {})),
        **font_tokens(spec.get("fonts")),
        **radius_tokens(spec.get("radius")),
        **(spec.get("tokens") or {}),
    }
    dark = {**color_tokens(colors.get("dark", {})), **(spec.get("dark") or {})}
    return light, dark


def _from_spec(key, spec, base):
    light, dark = _spec_tokens(spec)
    builtin = base is not None and base.key == key
    return Theme(
        key=key,
        label=str(spec.get("label", base.label if builtin else key.replace("_", " ").title())),
        note=str(spec.get("note", base.note if builtin else "")),
        layout=spec.get("layout", base.layout if base else "sidebar"),
        schemes=tuple(spec.get("schemes", base.schemes if base else ("light", "dark"))),
        swatch=tuple(spec.get("swatch", base.swatch if base else ("#fff", "#fff", "#000", "#000"))),
        extends="" if builtin else (base.key if base else "aurora"),
        tokens=light,
        dark=dark,
        default_scheme=spec.get("scheme", ""),
        density=spec.get("density", ""),
    )


def _configured():
    builtin = registry_builtin()
    themes = dict(builtin)
    for key, spec in (conf.get("THEMES") or {}).items():
        spec = spec or {}
        if spec.get("enabled") is False:
            themes.pop(key, None)
            continue
        base = builtin.get(key) or builtin.get(spec.get("extends", "aurora")) or builtin["aurora"]
        themes[key] = _from_spec(key, spec, base)
    order = conf.get("THEME_ORDER")
    if order:
        ranked = {k: i for i, k in enumerate(order)}
        themes = dict(sorted(themes.items(), key=lambda item: ranked.get(item[0], len(ranked))))
    return themes


def _custom_themes():
    return [t for t in _configured().values() if t.tokens or t.dark]


def registry_builtin():
    return {t.key: t for t in BUILTIN}


def registry():
    themes = _configured()
    if not themes:
        fallback = registry_builtin().get(conf.get("THEME")) or registry_builtin()["aurora"]
        themes = {fallback.key: fallback}
    return themes


def get_theme(key=None):
    themes = registry()
    return themes.get(key) or themes.get(conf.get("THEME")) or themes.get("aurora") or next(iter(themes.values()))


def read_prefs(request):
    raw = request.COOKIES.get("cc_admin_prefs", "") if request else ""
    try:
        data = json.loads(unquote(raw)) if raw else {}
    except ValueError:
        data = {}
    return data if isinstance(data, dict) else {}


def resolve(request):
    prefs = read_prefs(request) if conf.get("THEME_SWITCHER") else {}
    theme = get_theme(prefs.get("theme"))
    scheme = prefs.get("scheme") if prefs.get("scheme") in SCHEMES else (theme.default_scheme or conf.get("COLOR_SCHEME"))
    density = prefs.get("density") if prefs.get("density") in DENSITIES else (theme.density or conf.get("DENSITY"))
    layout = conf.get("LAYOUT") if conf.get("LAYOUT") in LAYOUTS else theme.layout
    return {
        "theme": theme,
        "scheme": theme.scheme_for(scheme),
        "density": density,
        "layout": layout,
        "forced_layout": conf.get("LAYOUT") in LAYOUTS,
    }


TOKEN_NAME = re.compile(r"^[a-z0-9-]+$")
HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
UNSAFE = re.compile(r"[;{}<>\\]")

COLOR_TOKENS = {
    "accent": "accent",
    "accent_hover": "accent-2",
    "on_accent": "accent-fg",
    "accent_text": "accent-text",
    "background": "bg",
    "background_2": "bg-2",
    "surface": "surface",
    "surface_2": "surface-2",
    "surface_3": "surface-3",
    "border": "border",
    "border_strong": "border-strong",
    "text": "text",
    "text_muted": "text-2",
    "text_subtle": "text-3",
    "success": "success",
    "warning": "warning",
    "danger": "danger",
    "info": "info",
    "sidebar": "side-bg",
    "sidebar_text": "side-text",
    "sidebar_active": "side-active",
    "sidebar_active_text": "side-active-text",
    "topbar": "top-bg",
    "input": "input-bg",
    "heatmap": "heat",
}

SANS = 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
SERIF = 'ui-serif, Georgia, "Times New Roman", serif'
MONO = 'ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace'

BUNDLED_FONTS = {
    "Geist": SANS,
    "Manrope": SANS,
    "DM Sans": SANS,
    "Figtree": SANS,
    "Plus Jakarta Sans": SANS,
    "IBM Plex Sans": SANS,
    "Nunito": SANS,
    "Archivo": SANS,
    "Space Grotesk": SANS,
    "Source Serif 4": SERIF,
    "Fraunces": SERIF,
    "Geist Mono": MONO,
    "JetBrains Mono": MONO,
    "IBM Plex Mono": MONO,
    "Space Mono": MONO,
}

USER_FONTS = ["Geist", "Manrope", "DM Sans", "Figtree", "Plus Jakarta Sans", "IBM Plex Sans", "Nunito", "Archivo", "Space Grotesk", "Source Serif 4", "JetBrains Mono", "system"]
RADII = {"sharp": "0px", "soft": "6px", "default": None, "round": "16px"}
SIZES = ("13", "14", "15", "16", "17")


def font_stack(name, fallback=SANS):
    if not name:
        return None
    name = str(name)
    if name == "system":
        return SANS
    if "," in name:
        return name
    return f'"{name}", {BUNDLED_FONTS.get(name, fallback)}'


def radius_tokens(value):
    if value is None:
        return {}
    if isinstance(value, (int, float)):
        value = f"{value}px"
    value = RADII.get(value, value) or None
    if value is None:
        return {}
    return {
        "radius": value,
        "radius-sm": f"calc({value} * .7)",
        "radius-lg": f"calc({value} * 1.4)",
        "btn-radius": f"calc({value} * .7)",
    }


def contrast(hex_color):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
    lum = 0.2126 * r**1.8 + 0.7152 * g**1.8 + 0.0722 * b**1.8
    return "#111111" if lum > 0.42 else "#ffffff"


def accent_tokens(color):
    tokens = {
        "accent": color,
        "accent-2": f"color-mix(in srgb, {color} 84%, black)",
        "accent-text": color,
        "chart-1": color,
        "heat": color,
    }
    if HEX.match(str(color)):
        tokens["accent-fg"] = contrast(color)
    return tokens


def color_tokens(colors):
    tokens = {}
    if colors.get("accent"):
        tokens.update(accent_tokens(colors["accent"]))
    for name, value in colors.items():
        if name in ("light", "dark", "accent"):
            continue
        if name == "chart" and isinstance(value, (list, tuple)):
            for i, color in enumerate(value[:6]):
                tokens[f"chart-{i + 1}"] = color
            continue
        tokens[COLOR_TOKENS.get(name, name)] = value
    return tokens


def font_tokens(fonts):
    if not isinstance(fonts, dict):
        return {}
    tokens = {}
    if fonts.get("body"):
        tokens["font"] = font_stack(fonts["body"])
    if fonts.get("heading"):
        tokens["font-head"] = font_stack(fonts["heading"])
    if fonts.get("mono"):
        tokens["font-mono"] = font_stack(fonts["mono"], MONO)
    if fonts.get("size"):
        size = fonts["size"]
        tokens["size"] = f"{size}px" if isinstance(size, (int, float)) else size
    return tokens


def _declarations(tokens):
    parts = []
    for name, value in tokens.items():
        name = str(name).replace("_", "-").lower()
        value = str(value)
        if TOKEN_NAME.match(name) and not UNSAFE.search(value):
            parts.append(f"--cc-{name}:{value}")
    return ";".join(parts)


def _split(tokens):
    light = {k: v for k, v in tokens.items() if k not in ("light", "dark")}
    light.update(tokens.get("light", {}))
    return light, dict(tokens.get("dark", {}))


def site_tokens():
    colors = conf.get("COLORS") or {}
    light, dark = _split(conf.get("TOKENS") or {})
    light = {**color_tokens({k: v for k, v in colors.items() if k not in ("light", "dark")}), **color_tokens(colors.get("light", {})), **font_tokens(conf.get("FONTS")), **radius_tokens(conf.get("RADIUS")), **light}
    dark = {**color_tokens(colors.get("dark", {})), **dark}
    return light, dark


def user_tokens(request):
    if request is None or not conf.get("THEME_SWITCHER"):
        return {}
    prefs = read_prefs(request)
    allowed = conf.get("APPEARANCE")
    tokens = {}
    accent = prefs.get("accent")
    if allowed.get("accent") and isinstance(accent, str) and HEX.match(accent):
        tokens.update(accent_tokens(accent))
    font = prefs.get("font")
    if allowed.get("font") and font in user_fonts():
        tokens["font"] = font_stack(font)
        tokens["font-head"] = font_stack(font)
    size = str(prefs.get("size", ""))
    if allowed.get("font_size") and size in SIZES:
        tokens["size"] = f"{size}px"
    radius = prefs.get("radius")
    if allowed.get("radius") and radius in RADII:
        tokens.update(radius_tokens(radius))
    return tokens


def user_fonts():
    fonts = conf.get("APPEARANCE").get("fonts")
    return list(fonts) if fonts else USER_FONTS


def token_css():
    blocks = []
    light, dark = site_tokens()
    if light:
        blocks.append(f"html.cc{{{_declarations(light)}}}")
    if dark:
        blocks.append(f"html.cc[data-scheme=dark]{{{_declarations(dark)}}}")
        blocks.append(f"@media (prefers-color-scheme:dark){{html.cc[data-scheme=auto]{{{_declarations(dark)}}}}}")
    for theme in _custom_themes():
        if theme.tokens:
            blocks.append(f"html.cc[data-skin={theme.key}]{{{_declarations(theme.tokens)}}}")
        if theme.dark:
            blocks.append(f"html.cc[data-skin={theme.key}][data-scheme=dark]{{{_declarations(theme.dark)}}}")
            blocks.append(
                f"@media (prefers-color-scheme:dark){{html.cc[data-skin={theme.key}][data-scheme=auto]{{{_declarations(theme.dark)}}}}}"
            )
    return "\n".join(blocks)


def user_css(request):
    mine = user_tokens(request)
    return f"html.cc[data-scheme][data-skin]{{{_declarations(mine)}}}" if mine else ""
