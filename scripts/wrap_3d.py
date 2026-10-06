#!/usr/bin/env python3
"""Put the 3D contribution calendar (yoshi389111/github-profile-3d-contrib output in profile-3d-contrib/)
inside the shared terminal frame. Writes assets/contrib-3d-{dark,light}.svg.

The source SVG is self-contained, so it nests as an inner <svg>. Its stylesheet is document-wide
once nested, so its `*` font rule is scoped to the inner svg, and its background colour is
swapped for the panel's so the frame reads as one surface.
"""
import re
import sys

from theme import ROOT, THEMES, prompt, window, write

W, PAD, TOP = 860, 10, 56
SOURCES = {"dark": "profile-night-green.svg", "light": "profile-green-animate.svg"}


def inner(svg_text, t):
    svg_text = re.sub(r"<\?xml[^>]*\?>", "", svg_text).strip()
    svg_text = re.sub(r"(<style[^>]*>\s*)\*\s*\{", r"\1.ext * {", svg_text, count=1)
    svg_text = re.sub(r"\.fill-bg\s*\{\s*fill:[^;]+;", f".fill-bg {{ fill: {t['bg']};", svg_text)
    svg_text = re.sub(r"\.stroke-bg\s*\{\s*stroke:[^;]+;", f".stroke-bg {{ stroke: {t['bg']};", svg_text)
    root = re.search(r"<svg\b[^>]*>", svg_text).group(0)
    _, _, vw, vh = (float(v) for v in re.search(r'viewBox="([^"]+)"', root).group(1).replace(",", " ").split())
    width = W - 2 * PAD
    height = width * vh / vw
    new_root = (f'<svg class="ext" xmlns="http://www.w3.org/2000/svg" x="{PAD}" y="{TOP}" '
                f'width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {vw:g} {vh:g}">')
    return svg_text.replace(root, new_root, 1), height


def main():
    src = ROOT / "profile-3d-contrib"
    missing = [f for f in SOURCES.values() if not (src / f).exists()]
    if missing:
        sys.exit(f"Missing {missing} in profile-3d-contrib/ — run the 3D contrib action first")
    for name, t in THEMES.items():
        art, gh = inner((src / SOURCES[name]).read_text(encoding="utf-8"), t)
        h = int(TOP + gh + 6)
        body = f'{prompt(t, 22, 44, "gh contributions --3d")}\n{art}'
        write("contrib-3d", name, window(t, W, h, "~/contributions — 3d", body, label="3D contribution calendar"))
    print("Wrote contrib-3d-{dark,light}.svg")


if __name__ == "__main__":
    main()
