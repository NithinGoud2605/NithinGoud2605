"""Shared look for every profile SVG: one terminal window frame, one font stack, two palettes.

Every generator renders once per theme and writes assets/<name>-dark.svg and assets/<name>-light.svg;
the README picks between them with <picture> and prefers-color-scheme.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

THEMES = {
    "dark": {
        "bg": "#0d1117", "border": "#30363d", "fg": "#c9d1d9", "bright": "#f0f6fc", "dim": "#8b949e",
        "green": "#39d353", "blue": "#58a6ff", "purple": "#bc8cff", "orange": "#ffa657", "red": "#ff7b72",
        "heat": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
    },
    "light": {
        "bg": "#ffffff", "border": "#d0d7de", "fg": "#1f2328", "bright": "#1f2328", "dim": "#59636e",
        "green": "#1a7f37", "blue": "#0969da", "purple": "#8250df", "orange": "#bc4c00", "red": "#cf222e",
        "heat": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
    },
}

FONT = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"


def base_css(t):
    return (
        # :not(.ext text) leaves nested third-party art (wrap_3d.py) to its own fonts and sizes.
        f"text:not(.ext text){{font-family:{FONT};font-size:13px;fill:{t['fg']}}}"
        f".dim{{fill:{t['dim']}}}.br{{fill:{t['bright']}}}.g{{fill:{t['green']}}}.b{{fill:{t['blue']}}}"
        f".pu{{fill:{t['purple']}}}.o{{fill:{t['orange']}}}.bold{{font-weight:700}}"
        ".fade{opacity:0;animation:fade .45s ease-out forwards}"
        "@keyframes fade{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}"
        ".cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.fade{animation:none;opacity:1}}"
    )


def window(t, w, h, title, body, css="", label=""):
    """Wrap body in the shared terminal window: rounded panel, traffic lights, centred title."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label or title)}">
<style>{base_css(t)}{css}</style>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="{t['bg']}" stroke="{t['border']}"/>
<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/><circle cx="50" cy="16" r="5" fill="#27c93f"/>
<text class="dim" x="{w / 2}" y="20" text-anchor="middle" style="font-size:11px">{escape(title)}</text>
{body}
</svg>
'''


def prompt(t, x, y, cmd, cls=""):
    return f'<text x="{x}" y="{y}" class="{cls}"><tspan class="g">$</tspan> <tspan class="br">{escape(cmd)}</tspan></text>'


def write(name, theme, svg):
    ASSETS.mkdir(exist_ok=True)
    path = ASSETS / f"{name}-{theme}.svg"
    path.write_text(svg, encoding="utf-8")
    return path


def fade(i, start=0.4, step=0.12):
    return f'style="animation-delay:{start + i * step:.2f}s"'
