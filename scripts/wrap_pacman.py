#!/usr/bin/env python3
"""Put the Pac-Man contribution game (abozanona/pacman-contribution-graph output in dist/) inside the
shared terminal frame, so it matches the other panels. Writes assets/pacman-{dark,light}.svg.

The game SVG is self-contained, so it nests as an inner <svg> scaled to the panel width.
"""
import re
import sys

from theme import ROOT, THEMES, prompt, window, write

W, PAD, TOP = 860, 18, 60
SOURCES = {"dark": "pacman-contribution-graph-dark.svg", "light": "pacman-contribution-graph.svg"}


def inner(svg_text):
    svg_text = re.sub(r"<\?xml[^>]*\?>", "", svg_text).strip()
    root = re.search(r"<svg\b[^>]*>", svg_text).group(0)
    vb = re.search(r'viewBox="([^"]+)"', root)
    if vb:
        _, _, vw, vh = (float(v) for v in vb.group(1).replace(",", " ").split())
    else:
        vw = float(re.search(r'width="([\d.]+)', root).group(1))
        vh = float(re.search(r'height="([\d.]+)', root).group(1))
    width = W - 2 * PAD
    height = width * vh / vw
    attrs = re.sub(r'\s(width|height|x|y|viewBox|preserveAspectRatio)="[^"]*"', "", root[4:-1])
    new_root = f'<svg x="{PAD}" y="{TOP}" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {vw:g} {vh:g}"{attrs}>'
    return svg_text.replace(root, new_root, 1), height


def main():
    dist = ROOT / "dist"
    missing = [f for f in SOURCES.values() if not (dist / f).exists()]
    if missing:
        sys.exit(f"Missing {missing} in dist/ — run the pacman action first")
    for name, t in THEMES.items():
        game, gh = inner((dist / SOURCES[name]).read_text(encoding="utf-8"))
        h = int(TOP + gh + 16)
        body = f'{prompt(t, 22, 44, "pacman --eat contributions")}\n{game}'
        write("pacman", name, window(t, W, h, "~/ — arcade", body, label="Pac-Man eating the contribution graph"))
    print("Wrote pacman-{dark,light}.svg")


if __name__ == "__main__":
    main()
