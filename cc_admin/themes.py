###############
# Qiyas Sadıqov CC
###############

import json
import re
from dataclasses import asdict, dataclass, field

from django.utils.html import escape

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


def _custom_themes():
    themes = []
    for key, spec in (conf.get("THEMES") or {}).items():
        base = registry_builtin().get(spec.get("extends", "aurora"))
        themes.append(
            Theme(
                key=key,
                label=spec.get("label", key.title()),
                note=spec.get("note", ""),
                layout=spec.get("layout", base.layout if base else "sidebar"),
                schemes=tuple(spec.get("schemes", base.schemes if base else ("light", "dark"))),
                swatch=tuple(spec.get("swatch", base.swatch if base else ("#fff", "#fff", "#000", "#000"))),
                extends=base.key if base else "aurora",
                tokens=spec.get("tokens", {}),
                dark=spec.get("dark", {}),
            )
        )
    return themes


def registry_builtin():
    return {t.key: t for t in BUILTIN}


def registry():
    themes = {t.key: t for t in BUILTIN}
    themes.update({t.key: t for t in _custom_themes()})
    return themes


def get_theme(key=None):
    themes = registry()
    return themes.get(key) or themes.get(conf.get("THEME")) or themes["aurora"]


def read_prefs(request):
    raw = request.COOKIES.get("cc_admin_prefs", "") if request else ""
    try:
        data = json.loads(raw) if raw else {}
    except ValueError:
        data = {}
    return data if isinstance(data, dict) else {}


def resolve(request):
    prefs = read_prefs(request) if conf.get("THEME_SWITCHER") else {}
    theme = get_theme(prefs.get("theme"))
    scheme = prefs.get("scheme") if prefs.get("scheme") in SCHEMES else conf.get("COLOR_SCHEME")
    density = prefs.get("density") if prefs.get("density") in DENSITIES else conf.get("DENSITY")
    layout = conf.get("LAYOUT") if conf.get("LAYOUT") in LAYOUTS else theme.layout
    return {
        "theme": theme,
        "scheme": theme.scheme_for(scheme),
        "density": density,
        "layout": layout,
        "forced_layout": conf.get("LAYOUT") in LAYOUTS,
    }


TOKEN_NAME = re.compile(r"^[a-z0-9-]+$")


def _declarations(tokens):
    parts = []
    for name, value in tokens.items():
        name = str(name).replace("_", "-").lower()
        if TOKEN_NAME.match(name):
            parts.append(f"--cc-{name}:{escape(str(value))}")
    return ";".join(parts)


def token_css():
    blocks = []
    global_tokens = conf.get("TOKENS") or {}
    light = {k: v for k, v in global_tokens.items() if k not in ("light", "dark")}
    light.update(global_tokens.get("light", {}))
    dark = dict(global_tokens.get("dark", {}))
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
