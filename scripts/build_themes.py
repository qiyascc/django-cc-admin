###############
# Qiyas Sadıqov CC
###############

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "cc_admin" / "static" / "cc_admin" / "css" / "themes.css"

DARK_SHADOWS = {
    "shadow-sm": "0 1px 2px rgb(0 0 0 / .4)",
    "shadow": "0 1px 2px rgb(0 0 0 / .35), 0 6px 18px -6px rgb(0 0 0 / .5)",
    "shadow-lg": "0 24px 70px -12px rgb(0 0 0 / .7), 0 0 0 1px rgb(255 255 255 / .06)",
    "backdrop": "rgb(0 0 0 / .6)",
    "color-scheme": "dark",
}

THEMES = {}


def theme(key, base, alt=None, extra="", base_scheme="light"):
    THEMES[key] = (base, alt, extra, base_scheme)


theme(
    "aurora",
    {},
    {
        **DARK_SHADOWS,
        "bg": "#0e0e12",
        "bg-2": "#121217",
        "surface": "#16161c",
        "surface-2": "#1c1c23",
        "surface-3": "#25252e",
        "border": "#25252e",
        "border-strong": "#34343f",
        "text": "#ececf1",
        "text-2": "#a4a4b3",
        "text-3": "#6f6f80",
        "accent": "#7b7bf2",
        "accent-2": "#9090f7",
        "accent-text": "#a8a8ff",
        "success": "#3ecf8e",
        "warning": "#f5a524",
        "danger": "#f2555a",
        "info": "#3ea8f5",
        "side-active": "#1c1c23",
        "side-active-shadow": "0 0 0 1px #2a2a34",
        "input-bg": "#121217",
        "th-bg": "#19191f",
        "heat-0": "#1f1f27",
        "card-shadow": "none",
    },
)

theme(
    "midnight",
    {
        **DARK_SHADOWS,
        "bg": "#070b14",
        "bg-2": "#0a101d",
        "surface": "#0d1424",
        "surface-2": "#111a2e",
        "surface-3": "#17223a",
        "border": "#1a2540",
        "border-strong": "#263457",
        "text": "#e2e8f0",
        "text-2": "#94a3b8",
        "text-3": "#5d6b85",
        "accent": "#22d3ee",
        "accent-2": "#67e8f9",
        "accent-fg": "#03222b",
        "accent-text": "#67e8f9",
        "success": "#34d399",
        "warning": "#fbbf24",
        "danger": "#fb7185",
        "info": "#60a5fa",
        "font": '"Space Grotesk", ui-sans-serif, system-ui, sans-serif',
        "font-mono": '"JetBrains Mono", ui-monospace, monospace',
        "head-weight": "600",
        "radius": "12px",
        "radius-lg": "16px",
        "side-bg": "#060912",
        "side-active": "rgb(34 211 238 / .08)",
        "side-active-text": "#e2e8f0",
        "side-active-shadow": "inset 2px 0 0 #22d3ee",
        "side-icon-active": "#22d3ee",
        "side-hover": "rgb(148 163 184 / .07)",
        "input-bg": "#0a1120",
        "th-bg": "#0f1729",
        "heat-0": "#131d33",
        "card-shadow": "none",
        "chart-2": "#a78bfa",
        "chart-3": "#f472b6",
        "chart-4": "#fbbf24",
        "chart-5": "#a3e635",
        "chart-6": "#60a5fa",
    },
    extra="""
& .cc-card, & .cc-fieldset, & .cc-changelist { background: linear-gradient(180deg, rgb(255 255 255 / .025), transparent 40%), var(--cc-surface); }
& .cc-kpi-value { text-shadow: 0 0 24px rgb(34 211 238 / .18); }
& .cc-brand-mark { background: linear-gradient(135deg, #22d3ee, #6366f1); color: #fff; }
& .cc-btn-primary { box-shadow: 0 0 0 1px #22d3ee, 0 6px 20px -6px rgb(34 211 238 / .55); }
& .cc-nav-item.is-active { border-radius: 0 var(--cc-radius-sm) var(--cc-radius-sm) 0; }
""",
)

theme(
    "paper",
    {
        "bg": "#f6f1e7",
        "bg-2": "#efe8da",
        "surface": "#fffdf8",
        "surface-2": "#f4eee2",
        "surface-3": "#ebe3d3",
        "border": "#e3dac8",
        "border-strong": "#d0c4ac",
        "text": "#2b2620",
        "text-2": "#665d50",
        "text-3": "#9a8f7e",
        "accent": "#b4442c",
        "accent-2": "#973721",
        "accent-text": "#a23c26",
        "success": "#3f7d4e",
        "warning": "#b7791f",
        "danger": "#b4442c",
        "info": "#2f6690",
        "font": '"IBM Plex Sans", ui-sans-serif, system-ui, sans-serif',
        "font-head": '"Source Serif 4", Georgia, "Times New Roman", serif',
        "font-mono": '"IBM Plex Mono", ui-monospace, monospace',
        "head-weight": "600",
        "head-track": "-0.01em",
        "h1": "34px",
        "radius": "4px",
        "radius-sm": "3px",
        "radius-lg": "6px",
        "shadow-sm": "none",
        "card-shadow": "none",
        "shadow": "0 1px 0 #e3dac8",
        "side-bg": "#f6f1e7",
        "side-active": "transparent",
        "side-active-shadow": "none",
        "th-bg": "#f7f2e8",
        "heat-0": "#ece5d6",
        "top-bg": "transparent",
        "chart-1": "#b4442c",
        "chart-2": "#2f6690",
        "chart-3": "#c98b2b",
        "chart-4": "#5b7f4f",
        "chart-5": "#7d5a8c",
        "chart-6": "#3a3a3a",
    },
    {
        **DARK_SHADOWS,
        "bg": "#1a1814",
        "bg-2": "#1f1c17",
        "surface": "#221f1a",
        "surface-2": "#2a261f",
        "surface-3": "#332e26",
        "border": "#37312a",
        "border-strong": "#4a4237",
        "text": "#ece4d6",
        "text-2": "#b5aa98",
        "text-3": "#7f7666",
        "accent": "#e07a5f",
        "accent-2": "#ea9077",
        "accent-fg": "#1a1814",
        "accent-text": "#ef9479",
        "side-bg": "#1a1814",
        "th-bg": "#26221c",
        "input-bg": "#1d1a16",
        "heat-0": "#2c2821",
        "shadow-sm": "none",
        "card-shadow": "none",
        "chart-6": "#d8cbb5",
    },
    extra="""
& .cc-side { border-bottom: 3px double var(--cc-border-strong); }
& .cc-titles h1 { font-style: italic; font-weight: 500; }
& .cc-eyebrow, & .cc-section-title { font-family: var(--cc-font-mono); letter-spacing: .12em; }
& .cc-card-head h2, & .cc-fieldset-head h2 { font-size: 18px; }
& .cc-nav-root .cc-nav-item, & .cc-nav-title { font-family: var(--cc-font-head); font-size: 15px !important; }
& .cc-kpi-value { font-size: 34px; }
& .cc-results tbody th a, & .cc-results tbody td > a:first-child:last-child { font-family: var(--cc-font-head); font-size: 15px; }
& .cc-brand-mark { border-radius: 50%; font-family: var(--cc-font-head); font-style: italic; font-size: 16px; }
""",
)

theme(
    "terminal",
    {
        **DARK_SHADOWS,
        "bg": "#050805",
        "bg-2": "#070b07",
        "surface": "#0a100a",
        "surface-2": "#0e160e",
        "surface-3": "#132013",
        "border": "#1b2e1b",
        "border-strong": "#2b472b",
        "text": "#c8f7c5",
        "text-2": "#82c27d",
        "text-3": "#4e7d4b",
        "accent": "#4ade80",
        "accent-2": "#86efac",
        "accent-fg": "#031a09",
        "accent-text": "#86efac",
        "success": "#4ade80",
        "warning": "#facc15",
        "danger": "#f87171",
        "info": "#22d3ee",
        "font": '"JetBrains Mono", ui-monospace, monospace',
        "font-head": '"JetBrains Mono", ui-monospace, monospace',
        "font-mono": '"JetBrains Mono", ui-monospace, monospace',
        "size": "13px",
        "head-weight": "700",
        "head-track": "-0.01em",
        "h1": "24px",
        "radius": "2px",
        "radius-sm": "2px",
        "radius-lg": "3px",
        "card-shadow": "none",
        "side-bg": "#040604",
        "side-active": "#0e1a0e",
        "side-active-shadow": "inset 0 0 0 1px #2b472b",
        "side-icon-active": "#4ade80",
        "input-bg": "#060a06",
        "th-bg": "#0c140c",
        "heat-0": "#0f1a0f",
        "heat": "#4ade80",
        "chart-2": "#facc15",
        "chart-3": "#22d3ee",
        "chart-4": "#f87171",
        "chart-5": "#c084fc",
        "chart-6": "#e5e7eb",
    },
    extra="""
& body::after { content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 999; background: repeating-linear-gradient(0deg, rgb(0 0 0 / .16) 0 1px, transparent 1px 3px); }
& .cc-titles h1::before { content: "> "; color: var(--cc-accent); }
& .cc-titles h1::after { content: "_"; color: var(--cc-accent); animation: cc-blink 1.1s steps(1) infinite; margin-left: 2px; }
& .cc-kpi-value, & .cc-model-count, & .cc-donut-center b { color: var(--cc-accent-2); text-shadow: 0 0 14px rgb(74 222 128 / .35); }
& .cc-badge { border-radius: 2px; text-transform: uppercase; letter-spacing: .05em; font-size: 10.5px; }
& .cc-badge::before { display: none; }
& .cc-nav-title, & .cc-eyebrow, & .cc-section-title, & .cc-th > span, & .cc-sort { text-transform: uppercase; }
& .cc-btn { text-transform: uppercase; letter-spacing: .04em; font-size: 12px; }
& .cc-brand-mark { background: transparent; color: var(--cc-accent); box-shadow: inset 0 0 0 1px var(--cc-accent); }
& .cc-card, & .cc-fieldset, & .cc-changelist { border-style: dashed; }
@keyframes cc-blink { 50% { opacity: 0; } }
""",
)

theme(
    "nord",
    {
        "bg": "#eceff4",
        "bg-2": "#e5e9f0",
        "surface": "#ffffff",
        "surface-2": "#f4f6f9",
        "surface-3": "#e9edf2",
        "border": "#dde2ea",
        "border-strong": "#c8cfda",
        "text": "#2e3440",
        "text-2": "#4c566a",
        "text-3": "#7b8597",
        "accent": "#5e81ac",
        "accent-2": "#4c6d96",
        "success": "#5e8a4a",
        "warning": "#c4783a",
        "danger": "#bf616a",
        "info": "#4f8ea4",
        "font": '"Figtree", ui-sans-serif, system-ui, sans-serif',
        "head-weight": "650",
        "radius": "8px",
        "radius-lg": "12px",
        "side-bg": "#e5e9f0",
        "th-bg": "#f4f6f9",
        "heat-0": "#e5e9f0",
        "chart-1": "#5e81ac",
        "chart-2": "#88c0d0",
        "chart-3": "#a3be8c",
        "chart-4": "#ebcb8b",
        "chart-5": "#b48ead",
        "chart-6": "#d08770",
    },
    {
        **DARK_SHADOWS,
        "bg": "#2e3440",
        "bg-2": "#2b303b",
        "surface": "#3b4252",
        "surface-2": "#434c5e",
        "surface-3": "#4c566a",
        "border": "#434c5e",
        "border-strong": "#56627a",
        "text": "#eceff4",
        "text-2": "#d8dee9",
        "text-3": "#9aa4b6",
        "accent": "#88c0d0",
        "accent-2": "#8fbcbb",
        "accent-fg": "#2e3440",
        "accent-text": "#88c0d0",
        "success": "#a3be8c",
        "warning": "#ebcb8b",
        "danger": "#bf616a",
        "info": "#81a1c1",
        "side-bg": "#2b303b",
        "side-active": "#3b4252",
        "side-active-shadow": "none",
        "input-bg": "#353c4a",
        "th-bg": "#3e4656",
        "heat-0": "#434c5e",
        "card-shadow": "none",
    },
)

theme(
    "brutal",
    {
        "bg": "#fff6d6",
        "bg-2": "#ffe9a8",
        "surface": "#ffffff",
        "surface-2": "#fff4c7",
        "surface-3": "#ffe68a",
        "border": "#000000",
        "border-strong": "#000000",
        "text": "#000000",
        "text-2": "#1f1f1f",
        "text-3": "#5a5a5a",
        "accent": "#ff5c35",
        "accent-2": "#ff7a57",
        "accent-fg": "#000000",
        "accent-text": "#d93a12",
        "accent-soft": "#ffd9cc",
        "success": "#00a86b",
        "warning": "#f5a300",
        "danger": "#e5233b",
        "info": "#2563eb",
        "font": '"Archivo", ui-sans-serif, system-ui, sans-serif',
        "font-head": '"Archivo", ui-sans-serif, system-ui, sans-serif',
        "font-mono": '"Space Mono", ui-monospace, monospace',
        "head-weight": "800",
        "head-track": "-0.03em",
        "h1": "34px",
        "radius": "6px",
        "radius-sm": "5px",
        "radius-lg": "8px",
        "border-w": "2px",
        "shadow-sm": "none",
        "shadow": "4px 4px 0 #000",
        "shadow-lg": "8px 8px 0 #000",
        "card-shadow": "5px 5px 0 #000",
        "side-bg": "#ffde59",
        "side-border": "#000000",
        "side-text": "#000000",
        "side-text-strong": "#000000",
        "side-title": "#000000",
        "side-icon": "#000000",
        "side-hover": "rgb(0 0 0 / .08)",
        "side-active": "#000000",
        "side-active-text": "#ffde59",
        "side-active-shadow": "none",
        "side-icon-active": "#ffde59",
        "input-border": "#000000",
        "th-bg": "#ffe68a",
        "grid-line": "#00000022",
        "heat-0": "#fff0b3",
        "row-hover": "#fff7d1",
        "row-selected": "#ffe0d6",
        "ring": "0 0 0 3px #000",
        "chart-1": "#ff5c35",
        "chart-2": "#2563eb",
        "chart-3": "#00a86b",
        "chart-4": "#9b5de5",
        "chart-5": "#f5a300",
        "chart-6": "#000000",
    },
    extra="""
& .cc-btn, & .cc-palette-trigger { box-shadow: 3px 3px 0 #000; font-weight: 700; }
& .cc-btn:hover { transform: translate(-1px, -1px); box-shadow: 4px 4px 0 #000; }
& .cc-btn:active { transform: translate(2px, 2px); box-shadow: 1px 1px 0 #000; }
& .cc-btn-primary { color: #000 !important; }
& .cc-badge { border: 1.5px solid #000; box-shadow: none; color: #000; background: color-mix(in srgb, var(--tone) 40%, #fff); font-weight: 700; }
& .cc-badge::before { background: var(--tone); box-shadow: 0 0 0 1.5px #000; }
& .cc-titles h1 { text-transform: uppercase; }
& .cc-kpi-value { font-size: 36px; font-weight: 900; }
& .cc-kpi:nth-child(4n+1) { background: #ffde59; }
& .cc-kpi:nth-child(4n+2) { background: #c3f0ff; }
& .cc-kpi:nth-child(4n+3) { background: #ffc8e6; }
& .cc-kpi:nth-child(4n+4) { background: #c9f7c1; }
& .cc-top { border-bottom: 2px solid #000; background: var(--cc-bg); }
& .cc-results thead th { border-bottom: 2px solid #000; }
& .cc-actionbar { border: 2px solid #000; box-shadow: 6px 6px 0 #000; background: #000; }
& .cc-brand-mark { background: #000; color: #ffde59; box-shadow: none; border-radius: 4px; }
& .cc-nav-group > ul .cc-nav-item.is-active { color: #000 !important; }
& .cc-tab.is-active { border-bottom-width: 4px; }
& .cc-env { border: 2px solid #000; color: #000; background: #ffde59; }
& .cc-login-art { --cc-login-bg: #ff5c35; --cc-login-fg: #000; border-right: 2px solid #000; }
""",
)

theme(
    "glass",
    {
        **DARK_SHADOWS,
        "bg": "#0b0820",
        "bg-2": "rgb(255 255 255 / .04)",
        "surface": "rgb(255 255 255 / .06)",
        "surface-2": "rgb(255 255 255 / .08)",
        "surface-3": "rgb(255 255 255 / .12)",
        "border": "rgb(255 255 255 / .11)",
        "border-strong": "rgb(255 255 255 / .2)",
        "text": "#f5f3ff",
        "text-2": "#c9c3e6",
        "text-3": "#8d86b3",
        "accent": "#a78bfa",
        "accent-2": "#c4b5fd",
        "accent-fg": "#1e1038",
        "accent-text": "#c4b5fd",
        "success": "#4ade80",
        "warning": "#fbbf24",
        "danger": "#fb7185",
        "info": "#67e8f9",
        "font": '"Manrope", ui-sans-serif, system-ui, sans-serif',
        "head-weight": "700",
        "radius": "12px",
        "radius-sm": "9px",
        "radius-lg": "18px",
        "glass": "blur(18px) saturate(1.5)",
        "side-bg": "rgb(255 255 255 / .05)",
        "side-active": "rgb(255 255 255 / .1)",
        "side-active-shadow": "inset 0 0 0 1px rgb(255 255 255 / .12)",
        "side-hover": "rgb(255 255 255 / .06)",
        "top-bg": "rgb(255 255 255 / .05)",
        "input-bg": "rgb(0 0 0 / .2)",
        "th-bg": "rgb(255 255 255 / .04)",
        "heat-0": "rgb(255 255 255 / .07)",
        "card-shadow": "0 10px 40px -12px rgb(0 0 0 / .5)",
        "menu-bg": "#1b1540",
        "chart-1": "#a78bfa",
        "chart-2": "#67e8f9",
        "chart-3": "#f9a8d4",
        "chart-4": "#fcd34d",
        "chart-5": "#86efac",
        "chart-6": "#93c5fd",
    },
    {
        "bg": "#eef0ff",
        "bg-2": "rgb(255 255 255 / .5)",
        "surface": "rgb(255 255 255 / .6)",
        "surface-2": "rgb(255 255 255 / .55)",
        "surface-3": "rgb(255 255 255 / .8)",
        "border": "rgb(255 255 255 / .85)",
        "border-strong": "rgb(120 110 200 / .25)",
        "text": "#1e1b3a",
        "text-2": "#4b4670",
        "text-3": "#8580a8",
        "accent": "#7c3aed",
        "accent-2": "#6d28d9",
        "accent-fg": "#ffffff",
        "accent-text": "#6d28d9",
        "side-bg": "rgb(255 255 255 / .45)",
        "side-active": "rgb(255 255 255 / .85)",
        "side-active-shadow": "0 4px 14px -6px rgb(80 60 160 / .3)",
        "side-hover": "rgb(255 255 255 / .5)",
        "top-bg": "rgb(255 255 255 / .4)",
        "input-bg": "rgb(255 255 255 / .7)",
        "th-bg": "rgb(255 255 255 / .4)",
        "heat-0": "rgb(255 255 255 / .7)",
        "card-shadow": "0 10px 40px -16px rgb(80 60 160 / .35)",
        "shadow-lg": "0 30px 80px -20px rgb(60 40 140 / .45)",
        "menu-bg": "#f7f5ff",
        "color-scheme": "light",
        "backdrop": "rgb(40 30 90 / .25)",
    },
    extra="""
& body { background: radial-gradient(1100px 700px at 8% -12%, #5b21b6 0%, transparent 60%), radial-gradient(900px 620px at 100% -5%, #0e7490 0%, transparent 55%), radial-gradient(1000px 700px at 65% 115%, #be185d 0%, transparent 55%), #0b0820; background-attachment: fixed; }
&alt body { background: radial-gradient(1100px 700px at 8% -12%, #c4b5fd 0%, transparent 60%), radial-gradient(900px 620px at 100% -5%, #a5f3fc 0%, transparent 55%), radial-gradient(1000px 700px at 65% 115%, #fbcfe8 0%, transparent 55%), #eef0ff; background-attachment: fixed; }
& .cc-menu, & .cc-palette-box, & .cc-theme-panel, & .cc-keys, & .cc-drawer, & .cc-confirm, & .cc-toast, & .calendarbox, & .clockbox, & .select2-dropdown, & .cc-chart-tip { background: var(--cc-menu-bg) !important; }
& .cc-palette-foot { background: rgb(255 255 255 / .03); }
& .cc-brand-mark { background: linear-gradient(135deg, #a78bfa, #22d3ee); color: #fff; }
& .cc-login-card { background: transparent; }
& .cc-login-art { --cc-login-bg: transparent; --cc-login-fg: #fff; }
& .cc-submit { background: rgb(20 14 50 / .55); }
&alt .cc-submit { background: rgb(255 255 255 / .6); }
& .cc-actionbar { background: #f5f3ff; color: #1e1038; }
""",
    base_scheme="dark",
)

theme(
    "slate",
    {
        "bg": "#f1f3f5",
        "bg-2": "#e9ecef",
        "surface": "#ffffff",
        "surface-2": "#f8f9fa",
        "surface-3": "#f1f3f5",
        "border": "#dee2e6",
        "border-strong": "#ced4da",
        "text": "#111827",
        "text-2": "#4b5563",
        "text-3": "#8b93a1",
        "accent": "#2563eb",
        "accent-2": "#1d4ed8",
        "success": "#15803d",
        "warning": "#b45309",
        "danger": "#dc2626",
        "info": "#0369a1",
        "font": '"IBM Plex Sans", ui-sans-serif, system-ui, sans-serif',
        "font-head": '"IBM Plex Sans", ui-sans-serif, system-ui, sans-serif',
        "font-mono": '"IBM Plex Mono", ui-monospace, monospace',
        "size": "13px",
        "head-weight": "600",
        "head-track": "-0.01em",
        "h1": "22px",
        "radius": "4px",
        "radius-sm": "4px",
        "radius-lg": "6px",
        "side-w": "240px",
        "side-bg": "#111827",
        "side-border": "#1f2937",
        "side-text": "#9ca3af",
        "side-text-strong": "#ffffff",
        "side-title": "#6b7280",
        "side-icon": "#6b7280",
        "side-icon-active": "#60a5fa",
        "side-hover": "rgb(255 255 255 / .06)",
        "side-active": "#1f2937",
        "side-active-text": "#ffffff",
        "side-active-shadow": "inset 2px 0 0 #3b82f6",
        "top-h": "52px",
        "row-y": "7px",
        "field-h": "34px",
        "pad": "22px",
        "gap": "14px",
        "th-bg": "#f8f9fa",
        "heat-0": "#eef1f4",
        "card-shadow": "none",
        "chart-1": "#2563eb",
        "chart-2": "#0891b2",
        "chart-3": "#d97706",
        "chart-4": "#7c3aed",
        "chart-5": "#16a34a",
        "chart-6": "#64748b",
    },
    {
        **DARK_SHADOWS,
        "bg": "#0b0f17",
        "bg-2": "#0e131c",
        "surface": "#111827",
        "surface-2": "#161e2e",
        "surface-3": "#1f2937",
        "border": "#1f2937",
        "border-strong": "#2d3a4f",
        "text": "#e5e7eb",
        "text-2": "#a3acb9",
        "text-3": "#6b7280",
        "accent": "#3b82f6",
        "accent-2": "#60a5fa",
        "accent-text": "#7cb0ff",
        "side-bg": "#080b11",
        "side-border": "#161e2e",
        "side-active": "#161e2e",
        "input-bg": "#0d1320",
        "th-bg": "#141c2b",
        "heat-0": "#1a2232",
        "card-shadow": "none",
    },
    extra="""
& .cc-th > span, & .cc-sort { text-transform: uppercase; font-size: 11px; letter-spacing: .05em; }
& .cc-results tbody td + td, & .cc-results tbody th + td { border-left: 1px solid var(--cc-border); }
& .cc-results thead th + th { border-left: 1px solid var(--cc-border); }
& .cc-kpi-value { font-size: 26px; }
& .cc-brand-mark { border-radius: 4px; background: #2563eb; }
& .cc-brand-text b { color: #fff; }
& .cc-side-search { background: rgb(255 255 255 / .06); color: #6b7280; }
& .cc-side-search input { color: #fff; }
& .cc-side-search:focus-within { background: rgb(255 255 255 / .1); }
& .cc-nav-item mark { color: #fff; }
& .cc-login-art { --cc-login-bg: #111827; --cc-login-fg: #fff; }
""",
)

theme(
    "sunset",
    {
        "bg": "#fff7f2",
        "bg-2": "#fff0e7",
        "surface": "#ffffff",
        "surface-2": "#fff4ee",
        "surface-3": "#ffe7da",
        "border": "#f6e2d7",
        "border-strong": "#ecccbb",
        "text": "#2a1712",
        "text-2": "#6e4c42",
        "text-3": "#a8867b",
        "accent": "#f0573a",
        "accent-2": "#d9472c",
        "accent-text": "#d9472c",
        "success": "#0f9f6e",
        "warning": "#e08a00",
        "danger": "#d6336c",
        "info": "#3b82f6",
        "font": '"DM Sans", ui-sans-serif, system-ui, sans-serif',
        "head-weight": "700",
        "radius": "12px",
        "radius-sm": "9px",
        "radius-lg": "18px",
        "side-bg": "linear-gradient(185deg, #ff8a4c 0%, #f0573a 38%, #c2255c 100%)",
        "side-border": "transparent",
        "side-text": "rgb(255 255 255 / .82)",
        "side-text-strong": "#ffffff",
        "side-title": "rgb(255 255 255 / .6)",
        "side-icon": "rgb(255 255 255 / .7)",
        "side-icon-active": "#f0573a",
        "side-hover": "rgb(255 255 255 / .14)",
        "side-active": "#ffffff",
        "side-active-text": "#2a1712",
        "side-active-shadow": "0 6px 16px -6px rgb(120 20 30 / .45)",
        "th-bg": "#fff8f4",
        "heat-0": "#ffeee4",
        "card-shadow": "0 1px 2px rgb(120 40 20 / .05), 0 8px 24px -14px rgb(120 40 20 / .18)",
        "chart-1": "#f0573a",
        "chart-2": "#f59f00",
        "chart-3": "#e64980",
        "chart-4": "#7950f2",
        "chart-5": "#12b886",
        "chart-6": "#339af0",
    },
    {
        **DARK_SHADOWS,
        "bg": "#170d0a",
        "bg-2": "#1d110d",
        "surface": "#221410",
        "surface-2": "#2b1a15",
        "surface-3": "#36221b",
        "border": "#3a251e",
        "border-strong": "#52352b",
        "text": "#fbeee8",
        "text-2": "#cfaea2",
        "text-3": "#8f7065",
        "accent": "#ff7a59",
        "accent-2": "#ff9175",
        "accent-fg": "#1a0d09",
        "accent-text": "#ff9175",
        "side-bg": "linear-gradient(185deg, #7c2d12 0%, #7f1d1d 50%, #4a0d2a 100%)",
        "side-active": "rgb(255 255 255 / .14)",
        "side-active-text": "#ffffff",
        "side-icon-active": "#ffb199",
        "side-active-shadow": "none",
        "input-bg": "#1c100c",
        "th-bg": "#271712",
        "heat-0": "#2e1c16",
        "card-shadow": "none",
    },
    extra="""
& .cc-brand-mark { background: #fff; color: #f0573a; }
& .cc-brand-text small { color: rgb(255 255 255 / .7); }
& .cc-side-search { background: rgb(255 255 255 / .16); color: rgb(255 255 255 / .75); }
& .cc-side-search input { color: #fff; }
& .cc-side-search input::placeholder { color: rgb(255 255 255 / .7); }
& .cc-side-foot { border-top-color: rgb(255 255 255 / .18); }
& .cc-nav-item .cc-badge { background: rgb(255 255 255 / .92); }
& .cc-kpi { overflow: hidden; }
& .cc-kpi::after { content: ""; position: absolute; width: 140px; height: 140px; right: -50px; top: -60px; border-radius: 50%; background: radial-gradient(circle, color-mix(in srgb, var(--cc-accent) 16%, transparent), transparent 70%); }
& .cc-login-art { --cc-login-bg: linear-gradient(160deg, #ff8a4c, #f0573a 40%, #c2255c); background: var(--cc-login-bg); --cc-login-fg: #fff; }
""",
)

theme(
    "forest",
    {
        "bg": "#f3f1ea",
        "bg-2": "#ece9df",
        "surface": "#fbfaf6",
        "surface-2": "#f2efe6",
        "surface-3": "#e9e5d8",
        "border": "#e1dccd",
        "border-strong": "#cfc8b4",
        "text": "#1f2a22",
        "text-2": "#4e5d51",
        "text-3": "#899487",
        "accent": "#2f6b4f",
        "accent-2": "#24563f",
        "accent-text": "#2a6148",
        "success": "#3d7f4f",
        "warning": "#b7791f",
        "danger": "#b5443b",
        "info": "#3b6d8f",
        "font": '"Figtree", ui-sans-serif, system-ui, sans-serif',
        "font-head": '"Fraunces", Georgia, serif',
        "head-weight": "600",
        "head-track": "-0.015em",
        "h1": "30px",
        "radius": "10px",
        "radius-lg": "14px",
        "side-bg": "#1f3a2c",
        "side-border": "#1f3a2c",
        "side-text": "#bcd1c2",
        "side-text-strong": "#ffffff",
        "side-title": "#7fa08b",
        "side-icon": "#7fa08b",
        "side-icon-active": "#b7e4c7",
        "side-hover": "rgb(255 255 255 / .06)",
        "side-active": "rgb(255 255 255 / .1)",
        "side-active-text": "#ffffff",
        "side-active-shadow": "none",
        "th-bg": "#f5f3ec",
        "heat-0": "#e8e4d6",
        "heat": "#2f6b4f",
        "chart-1": "#2f6b4f",
        "chart-2": "#b58b3d",
        "chart-3": "#7aa874",
        "chart-4": "#9b5e3c",
        "chart-5": "#4f7c8a",
        "chart-6": "#c4b48a",
    },
    {
        **DARK_SHADOWS,
        "bg": "#0e1510",
        "bg-2": "#111a14",
        "surface": "#141e17",
        "surface-2": "#1a261d",
        "surface-3": "#213025",
        "border": "#223127",
        "border-strong": "#30453a",
        "text": "#e3ece5",
        "text-2": "#a6b9ab",
        "text-3": "#6b8170",
        "accent": "#6fbf95",
        "accent-2": "#8ad0aa",
        "accent-fg": "#0b1a11",
        "accent-text": "#8ad0aa",
        "side-bg": "#0a110c",
        "side-border": "#16211a",
        "input-bg": "#111a14",
        "th-bg": "#172119",
        "heat-0": "#1b281f",
        "heat": "#6fbf95",
        "card-shadow": "none",
    },
    extra="""
& .cc-brand-mark { background: #b7e4c7; color: #1f3a2c; font-family: var(--cc-font-head); font-size: 16px; }
& .cc-brand-text b { font-family: var(--cc-font-head); color: #fff; font-size: 17px; }
& .cc-brand-text small { color: #7fa08b; }
& .cc-side-search { background: rgb(255 255 255 / .07); color: #7fa08b; }
& .cc-side-search input { color: #fff; }
& .cc-side-foot { border-top-color: rgb(255 255 255 / .08); }
& .cc-kpi-value, & .cc-model-count, & .cc-donut-center b, & .cc-chart-summary b { font-family: var(--cc-font-head); font-weight: 500; }
& .cc-card-head h2, & .cc-fieldset-head h2 { font-size: 17px; }
& .cc-login-art { --cc-login-bg: #1f3a2c; --cc-login-fg: #e8f3ec; }
""",
)

theme(
    "mono",
    {
        "bg": "#ffffff",
        "bg-2": "#fafafa",
        "surface": "#ffffff",
        "surface-2": "#fafafa",
        "surface-3": "#f2f2f2",
        "border": "#eaeaea",
        "border-strong": "#d4d4d4",
        "text": "#000000",
        "text-2": "#525252",
        "text-3": "#8f8f8f",
        "accent": "#000000",
        "accent-2": "#2b2b2b",
        "accent-fg": "#ffffff",
        "accent-text": "#000000",
        "accent-soft": "#f2f2f2",
        "success": "#1a7f37",
        "warning": "#9a6700",
        "danger": "#cf222e",
        "info": "#525252",
        "neutral": "#525252",
        "font": '"Geist", ui-sans-serif, system-ui, sans-serif',
        "font-mono": '"Geist Mono", ui-monospace, monospace',
        "head-weight": "600",
        "head-track": "-0.04em",
        "h1": "32px",
        "radius": "6px",
        "radius-sm": "6px",
        "radius-lg": "8px",
        "shadow-sm": "none",
        "card-shadow": "none",
        "side-bg": "#ffffff",
        "side-active": "transparent",
        "side-active-shadow": "none",
        "th-bg": "#fafafa",
        "heat-0": "#f0f0f0",
        "heat": "#000000",
        "row-hover": "#fafafa",
        "row-selected": "#f2f2f2",
        "ring": "0 0 0 3px rgb(0 0 0 / .12)",
        "chart-1": "#000000",
        "chart-2": "#8f8f8f",
        "chart-3": "#c9c9c9",
        "chart-4": "#525252",
        "chart-5": "#e5e5e5",
        "chart-6": "#2b2b2b",
    },
    {
        **DARK_SHADOWS,
        "bg": "#000000",
        "bg-2": "#0a0a0a",
        "surface": "#0a0a0a",
        "surface-2": "#111111",
        "surface-3": "#1a1a1a",
        "border": "#1f1f1f",
        "border-strong": "#333333",
        "text": "#ededed",
        "text-2": "#a1a1a1",
        "text-3": "#6b6b6b",
        "accent": "#ffffff",
        "accent-2": "#d4d4d4",
        "accent-fg": "#000000",
        "accent-text": "#ffffff",
        "accent-soft": "#1a1a1a",
        "neutral": "#a1a1a1",
        "info": "#a1a1a1",
        "side-bg": "#000000",
        "input-bg": "#0a0a0a",
        "th-bg": "#0a0a0a",
        "heat-0": "#161616",
        "heat": "#ffffff",
        "row-hover": "#0f0f0f",
        "row-selected": "#161616",
        "ring": "0 0 0 3px rgb(255 255 255 / .2)",
        "card-shadow": "none",
        "chart-1": "#ffffff",
        "chart-2": "#8f8f8f",
        "chart-3": "#4d4d4d",
        "chart-4": "#bdbdbd",
        "chart-5": "#2b2b2b",
        "chart-6": "#e5e5e5",
    },
    extra="""
& .cc-brand-mark { background: var(--cc-text); color: var(--cc-bg); border-radius: 50%; box-shadow: none; }
& .cc-kpi-icon, & .cc-card-icon, & .cc-model-icon { background: transparent; color: var(--cc-text); box-shadow: inset 0 0 0 1px var(--cc-border); }
& .cc-badge { background: transparent; box-shadow: inset 0 0 0 1px var(--cc-border-strong); color: var(--cc-text); }
& .cc-badge::before { background: var(--tone); }
& .cc-eyebrow { font-family: var(--cc-font-mono); letter-spacing: .02em; text-transform: none; }
& .cc-kpi-value { font-size: 34px; letter-spacing: -0.05em; }
& .cc-login-art { --cc-login-bg: var(--cc-text); --cc-login-fg: var(--cc-bg); }
""",
)

theme(
    "rose",
    {
        "bg": "#fdf2f6",
        "bg-2": "#fbe9f0",
        "surface": "#ffffff",
        "surface-2": "#fdf1f6",
        "surface-3": "#fbe4ee",
        "border": "#f6dae6",
        "border-strong": "#edc2d5",
        "text": "#3b0a22",
        "text-2": "#7a4b62",
        "text-3": "#b0889b",
        "accent": "#db2777",
        "accent-2": "#be185d",
        "accent-text": "#c0206a",
        "success": "#0d9488",
        "warning": "#d97706",
        "danger": "#e11d48",
        "info": "#7c3aed",
        "font": '"Nunito", ui-sans-serif, system-ui, sans-serif',
        "head-weight": "800",
        "head-track": "-0.02em",
        "radius": "16px",
        "radius-sm": "12px",
        "radius-lg": "22px",
        "btn-radius": "999px",
        "side-bg": "#ffffff",
        "side-border": "#f6dae6",
        "side-active": "#fdf1f6",
        "side-active-shadow": "none",
        "side-icon-active": "#db2777",
        "th-bg": "#fff7fa",
        "heat-0": "#fbe4ee",
        "card-shadow": "0 10px 30px -18px rgb(190 24 93 / .35)",
        "chart-1": "#db2777",
        "chart-2": "#8b5cf6",
        "chart-3": "#f59e0b",
        "chart-4": "#14b8a6",
        "chart-5": "#f472b6",
        "chart-6": "#6366f1",
    },
    {
        **DARK_SHADOWS,
        "bg": "#170a11",
        "bg-2": "#1d0d16",
        "surface": "#22101a",
        "surface-2": "#2b1521",
        "surface-3": "#371b2a",
        "border": "#3a1d2c",
        "border-strong": "#55293f",
        "text": "#fde8f1",
        "text-2": "#d4a6bb",
        "text-3": "#93687c",
        "accent": "#f472b6",
        "accent-2": "#f9a8d4",
        "accent-fg": "#2a0a19",
        "accent-text": "#f9a8d4",
        "side-bg": "#1d0d16",
        "side-border": "#2b1521",
        "side-active": "#2b1521",
        "input-bg": "#1b0b14",
        "th-bg": "#26121d",
        "heat-0": "#2e1622",
        "card-shadow": "none",
    },
    extra="""
& .cc-brand-mark { border-radius: 50%; background: linear-gradient(135deg, #f472b6, #db2777); }
& .cc-nav-item { border-radius: 999px; }
& .cc-search-box, & .cc-palette-trigger, & .cc-side-search { border-radius: 999px; }
& .cc-kpi-icon, & .cc-card-icon, & .cc-model-icon, & .cc-list-icon { border-radius: 50%; }
& .cc-chip { border-radius: 999px; }
& .cc-login-art { --cc-login-bg: linear-gradient(150deg, #f9a8d4, #db2777 60%, #9d174d); background: var(--cc-login-bg); --cc-login-fg: #fff; }
""",
)

theme(
    "ocean",
    {
        "bg": "#f0f7f8",
        "bg-2": "#e6f1f3",
        "surface": "#ffffff",
        "surface-2": "#f3f9fa",
        "surface-3": "#e7f2f4",
        "border": "#d9e9ec",
        "border-strong": "#c1d9de",
        "text": "#0b2a33",
        "text-2": "#3d5f68",
        "text-3": "#7d9aa2",
        "accent": "#0e8a8a",
        "accent-2": "#0b7272",
        "accent-text": "#0b7c7c",
        "success": "#0f9f6e",
        "warning": "#d97706",
        "danger": "#e5484d",
        "info": "#0284c7",
        "font": '"Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif',
        "head-weight": "700",
        "radius": "10px",
        "radius-lg": "14px",
        "side-bg": "#0b2a33",
        "side-border": "#0b2a33",
        "side-text": "#a7c7cc",
        "side-text-strong": "#ffffff",
        "side-title": "#5f8b93",
        "side-icon": "#7fb0b7",
        "side-icon-active": "#5eead4",
        "side-hover": "rgb(255 255 255 / .07)",
        "side-active": "rgb(94 234 212 / .12)",
        "side-active-text": "#ffffff",
        "side-active-shadow": "none",
        "th-bg": "#f5fafb",
        "heat-0": "#e3eff1",
        "chart-1": "#0e8a8a",
        "chart-2": "#0284c7",
        "chart-3": "#f59e0b",
        "chart-4": "#14b8a6",
        "chart-5": "#6366f1",
        "chart-6": "#f43f5e",
    },
    {
        **DARK_SHADOWS,
        "bg": "#061a20",
        "bg-2": "#071e25",
        "surface": "#0a242c",
        "surface-2": "#0d2d36",
        "surface-3": "#123842",
        "border": "#123842",
        "border-strong": "#1b4b57",
        "text": "#e2f3f5",
        "text-2": "#9cc3c9",
        "text-3": "#5f8a91",
        "accent": "#2dd4bf",
        "accent-2": "#5eead4",
        "accent-fg": "#042f2e",
        "accent-text": "#5eead4",
        "side-bg": "#04141a",
        "side-border": "#0a242c",
        "input-bg": "#081f26",
        "th-bg": "#0c2a32",
        "heat-0": "#0f2f38",
        "card-shadow": "none",
    },
    extra="""
& .cc-brand-mark { background: linear-gradient(135deg, #5eead4, #0e8a8a); color: #042f2e; }
& .cc-brand-text b { color: #fff; }
& .cc-brand-text small { color: #5f8b93; }
& .cc-side-search { background: rgb(255 255 255 / .07); color: #7fb0b7; }
& .cc-side-search input { color: #fff; }
& .cc-side-foot { border-top-color: rgb(255 255 255 / .08); }
& .cc-login-art { --cc-login-bg: linear-gradient(160deg, #0b2a33, #0e8a8a); background: var(--cc-login-bg); --cc-login-fg: #e2f3f5; }
""",
)

theme(
    "classic",
    {
        "bg": "#008080",
        "bg-2": "#c0c0c0",
        "surface": "#c0c0c0",
        "surface-2": "#c0c0c0",
        "surface-3": "#d4d0c8",
        "border": "#808080",
        "border-strong": "#404040",
        "text": "#000000",
        "text-2": "#202020",
        "text-3": "#505050",
        "accent": "#000080",
        "accent-2": "#1084d0",
        "accent-fg": "#ffffff",
        "accent-text": "#000080",
        "accent-soft": "#d4d0c8",
        "success": "#008000",
        "warning": "#806000",
        "danger": "#c00000",
        "info": "#000080",
        "neutral": "#404040",
        "font": 'Tahoma, "MS Sans Serif", Geneva, Verdana, sans-serif',
        "font-head": 'Tahoma, "MS Sans Serif", Geneva, Verdana, sans-serif',
        "font-mono": '"Courier New", Courier, monospace',
        "size": "12.5px",
        "head-weight": "700",
        "head-track": "0",
        "h1": "22px",
        "radius": "0",
        "radius-sm": "0",
        "radius-lg": "0",
        "btn-radius": "0",
        "border-w": "2px",
        "shadow-sm": "none",
        "shadow": "1px 1px 0 #000",
        "shadow-lg": "2px 2px 0 #000",
        "card-shadow": "1px 1px 0 #000",
        "side-bg": "#c0c0c0",
        "side-border": "#808080",
        "side-text": "#000000",
        "side-text-strong": "#000000",
        "side-title": "#404040",
        "side-icon": "#000000",
        "side-icon-active": "#ffffff",
        "side-hover": "rgb(0 0 128 / .12)",
        "side-active": "#000080",
        "side-active-text": "#ffffff",
        "side-active-shadow": "none",
        "top-bg": "#c0c0c0",
        "input-bg": "#ffffff",
        "input-border": "#808080",
        "th-bg": "#c0c0c0",
        "grid-line": "#808080",
        "heat-0": "#ffffff",
        "heat": "#000080",
        "row-hover": "#e8e8e8",
        "row-selected": "#000080",
        "ring": "0 0 0 1px #000",
        "backdrop": "rgb(0 0 0 / .25)",
        "chart-1": "#000080",
        "chart-2": "#008080",
        "chart-3": "#808000",
        "chart-4": "#800080",
        "chart-5": "#008000",
        "chart-6": "#800000",
    },
    extra="""
& .cc-card, & .cc-fieldset, & .cc-changelist, & .cc-menu, & .cc-palette-box, & .cc-theme-panel, & .cc-keys, & .cc-drawer, & .cc-confirm, & .cc-toast, & .cc-submit, & .cc-side, & .cc-btn, & .cc-palette-trigger, & .cc-actionbar, & .calendarbox, & .clockbox { border-style: solid; border-width: 2px; border-color: #ffffff #808080 #808080 #ffffff; box-shadow: 1px 1px 0 #000; background-color: #c0c0c0; }
& .cc-results tbody, & .cc-table-wrap { background: #fff; }
& .cc-changelist .cc-table-wrap { margin: 0 6px; border: 2px solid; border-color: #808080 #fff #fff #808080; box-shadow: inset 1px 1px 0 #000; }
& .cc-btn:active { border-color: #808080 #fff #fff #808080; box-shadow: inset 1px 1px 0 #000; }
& .cc-btn-primary { background-color: #c0c0c0; color: #000 !important; outline: 1px solid #000; outline-offset: -4px; }
& .cc-content input:is([type=text], [type=email], [type=url], [type=password], [type=number], [type=search], [type=tel], [type=date], [type=time]), & .cc-content select, & .cc-content textarea, & .cc-search-box { border-style: solid !important; border-width: 2px !important; border-color: #808080 #ffffff #ffffff #808080 !important; box-shadow: inset 1px 1px 0 #000 !important; }
& .cc-card > .cc-card-head, & .cc-fieldset-head, & .cc-panel-head { margin: -20px -20px 14px; padding: 4px 6px 4px 8px; background: linear-gradient(90deg, #000080, #1084d0); color: #fff; align-items: center; }
& .cc-fieldset-head { margin: 0; }
& .cc-card > .cc-card-head h2, & .cc-fieldset-head h2, & .cc-fieldset-head h3, & .cc-fieldset-head h4, & .cc-panel-head b { color: #fff; font-size: 12.5px; }
& .cc-card > .cc-card-head p, & .cc-panel-head small { color: #dfe8ff; }
& .cc-card > .cc-card-head a { color: #fff; }
& .cc-card > .cc-card-head .cc-card-icon { display: none; }
& .cc-panel-head { margin: 0 0 12px; }
& .cc-panel-head .cc-icon-btn { color: #000; background: #c0c0c0; width: 20px; height: 18px; border: 2px solid; border-color: #fff #808080 #808080 #fff; border-radius: 0; margin: 0; }
& .cc-titles h1, & .cc-titles .cc-lead, & .cc-titles .cc-eyebrow, & .cc-section-title { color: #fff !important; text-shadow: 1px 1px 0 #000; }
& .cc-tabs { border-bottom-color: #fff; }
& .cc-tab { color: #e0f0f0 !important; }
& .cc-tab.is-active { color: #fff !important; border-bottom-color: #fff; }
& .cc-form-tabs .cc-tab, & .cc-tabs-page .cc-tab { background: #c0c0c0; color: #000 !important; border: 2px solid; border-color: #fff #808080 transparent #fff; margin-right: 2px; padding: 5px 12px; }
& .cc-form-tabs .cc-tab.is-active, & .cc-tabs-page .cc-tab.is-active { background: #c0c0c0; position: relative; top: 2px; padding-bottom: 7px; }
& .cc-top { border-top: 2px solid #fff; box-shadow: inset 0 -1px 0 #808080; backdrop-filter: none; }
& .cc-crumbs a { color: #000080; }
& .cc-results tbody tr.selected, & .cc-results tbody tr.selected * { color: #fff !important; }
& .cc-badge { border-radius: 0; box-shadow: none; border: 1px solid #000; background: #fff; color: #000; }
& .cc-badge::before { border-radius: 0; background: var(--tone); }
& .cc-brand-mark { background: #000080; color: #fff; border-radius: 0; box-shadow: none; }
& .cc-avatar { border-radius: 0; }
& .cc-kpi-icon, & .cc-card-icon, & .cc-model-icon, & .cc-list-icon { border-radius: 0; background: #fff; color: #000080; border: 1px solid #808080; }
& .cc-progress { border-radius: 0; background: #fff; border: 1px solid #808080; height: 14px; }
& .cc-progress i { border-radius: 0; background: repeating-linear-gradient(90deg, #000080 0 8px, transparent 8px 10px); }
& .cc-delta { border-radius: 0; }
& .cc-heat-grid i, & .cc-heat-legend i { border-radius: 0; }
& .cc-actionbar { color: #000; }
& .cc-actionbar .cc-icon-btn { color: #000; }
& .cc-actionbar select { color: #000 !important; background-color: #fff !important; }
& .cc-dialog::backdrop { backdrop-filter: none; }
& .cc-login-art { --cc-login-bg: #008080; --cc-login-fg: #fff; }
& .cc-login-card { background: #c0c0c0; }
& .cc-nav-item { border-radius: 0; }
& .cc-nav-title { color: #000; }
& .cc-env { border-radius: 0; border: 1px solid #000; }
""",
)

theme(
    "cc",
    {
        **DARK_SHADOWS,
        "bg": "#0c1014",
        "bg-2": "#0f1418",
        "surface": "#11171c",
        "surface-2": "#161d23",
        "surface-3": "#1c242c",
        "border": "rgb(237 241 243 / .09)",
        "border-strong": "rgb(237 241 243 / .17)",
        "text": "#edf1f3",
        "text-2": "#8a99a4",
        "text-3": "#5d6b76",
        "accent": "#8fb4cc",
        "accent-2": "#a9c6d9",
        "accent-fg": "#0c1014",
        "accent-text": "#a9c6d9",
        "success": "#7fc79a",
        "warning": "#d9b36c",
        "danger": "#e07a7a",
        "info": "#8fb4cc",
        "neutral": "#8a99a4",
        "font": '"Geist", ui-sans-serif, system-ui, sans-serif',
        "font-mono": '"Geist Mono", ui-monospace, monospace',
        "head-weight": "600",
        "head-track": "-0.035em",
        "h1": "30px",
        "radius": "6px",
        "radius-sm": "5px",
        "radius-lg": "8px",
        "card-shadow": "none",
        "side-bg": "#0c1014",
        "side-active": "rgb(143 180 204 / .09)",
        "side-active-shadow": "inset 0 0 0 1px rgb(143 180 204 / .18)",
        "side-icon-active": "#8fb4cc",
        "side-hover": "rgb(237 241 243 / .05)",
        "input-bg": "#0e1317",
        "th-bg": "#121920",
        "heat-0": "rgb(237 241 243 / .07)",
        "heat": "#8fb4cc",
        "chart-1": "#8fb4cc",
        "chart-2": "#edf1f3",
        "chart-3": "#c9a96e",
        "chart-4": "#5f7f94",
        "chart-5": "#7fa889",
        "chart-6": "#b98aa8",
    },
    {
        "bg": "#edf1f3",
        "bg-2": "#e5eaed",
        "surface": "#ffffff",
        "surface-2": "#f4f6f8",
        "surface-3": "#e9eef1",
        "border": "rgb(12 16 20 / .09)",
        "border-strong": "rgb(12 16 20 / .17)",
        "text": "#0c1014",
        "text-2": "#4d5c67",
        "text-3": "#87949e",
        "accent": "#3f6f8f",
        "accent-2": "#335c78",
        "accent-fg": "#ffffff",
        "accent-text": "#3f6f8f",
        "success": "#3d8a5b",
        "warning": "#a87b1f",
        "danger": "#c24848",
        "info": "#3f6f8f",
        "neutral": "#4d5c67",
        "side-bg": "#edf1f3",
        "side-active": "#ffffff",
        "side-active-shadow": "0 0 0 1px rgb(12 16 20 / .09)",
        "side-icon-active": "#3f6f8f",
        "side-hover": "rgb(12 16 20 / .04)",
        "input-bg": "#ffffff",
        "th-bg": "#f4f6f8",
        "heat-0": "rgb(12 16 20 / .06)",
        "heat": "#3f6f8f",
        "color-scheme": "light",
        "shadow-sm": "0 1px 2px rgb(12 16 20 / .05)",
        "shadow": "0 1px 2px rgb(12 16 20 / .04), 0 4px 14px -4px rgb(12 16 20 / .08)",
        "shadow-lg": "0 24px 60px -12px rgb(12 16 20 / .25)",
        "backdrop": "rgb(12 16 20 / .4)",
        "chart-1": "#3f6f8f",
        "chart-2": "#0c1014",
        "chart-3": "#b08a46",
        "chart-4": "#87a7bd",
        "chart-5": "#5f8f6c",
        "chart-6": "#9c6f8c",
    },
    extra="""
& .cc-eyebrow, & .cc-section-title, & .cc-nav-title, & .cc-th > span, & .cc-sort, & .cc-panel-label, & .cc-palette-group { font-family: var(--cc-font-mono); letter-spacing: .14em !important; font-size: 10.5px !important; text-transform: uppercase; font-weight: 500 !important; }
& .cc-eyebrow::before { content: "( "; }
& .cc-eyebrow::after { content: " )"; }
& .cc-brand-mark { background: transparent; color: var(--cc-accent); box-shadow: inset 0 0 0 1px var(--cc-border-strong); font-family: var(--cc-font-mono); font-weight: 500; letter-spacing: .04em; }
& .cc-kpi-value { font-size: 34px; letter-spacing: -0.045em; }
& .cc-kpi-title, & .cc-chart-summary span, & .cc-donut-center span { font-family: var(--cc-font-mono); font-size: 11px; letter-spacing: .1em; text-transform: uppercase; }
& .cc-kpi-icon, & .cc-card-icon, & .cc-model-icon { background: transparent; box-shadow: inset 0 0 0 1px var(--cc-border-strong); color: var(--cc-accent); }
& .cc-badge { border-radius: 4px; font-family: var(--cc-font-mono); font-weight: 500; font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase; }
& .cc-btn { font-weight: 500; }
& .cc-login-art { --cc-login-bg: #0c1014; --cc-login-fg: #edf1f3; border-right: 1px solid var(--cc-border); }
& .cc-login-deco i { border-color: rgb(143 180 204 / .2); }
""",
    base_scheme="dark",
)

DENSITY = (
    ':where(html.cc[data-density="compact"]){--cc-row-y:6px;--cc-field-h:32px;--cc-pad:20px;--cc-gap:12px;--cc-size:13px}\n'
    ':where(html.cc[data-density="spacious"]){--cc-row-y:15px;--cc-field-h:42px;--cc-pad:36px;--cc-gap:24px}\n'
)


def block(selector, tokens):
    if not tokens:
        return ""
    body = "".join(f"--cc-{k}:{v};" if k != "color-scheme" else f"color-scheme:{v};" for k, v in tokens.items())
    return f"{selector}{{{body}}}\n"


def build():
    out = []
    for key, (base, alt, extra, base_scheme) in THEMES.items():
        alt_scheme = "light" if base_scheme == "dark" else "dark"
        sel = f'html.cc[data-theme="{key}"]'
        alt_sel = f'html.cc[data-theme="{key}"][data-scheme="{alt_scheme}"]'
        auto_sel = f'html.cc[data-theme="{key}"][data-scheme="auto"]'
        media = f"@media (prefers-color-scheme: {alt_scheme}){{"
        out.append(block(f":where({sel})", base))
        if alt:
            out.append(block(f":where({alt_sel})", alt))
            out.append(media + block(f":where({auto_sel})", alt).strip() + "}\n")
        for line in extra.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("@keyframes"):
                out.append(line + "\n")
                continue
            if "&alt" in line:
                if not alt:
                    continue
                out.append(line.replace("&alt", alt_sel) + "\n")
                out.append(media + line.replace("&alt", auto_sel) + "}\n")
            else:
                out.append(line.replace("&", sel) + "\n")
    out.append(DENSITY)
    OUT.write_text("".join(out), encoding="utf-8")
    return OUT


if __name__ == "__main__":
    path = build()
    print(path, path.stat().st_size)
