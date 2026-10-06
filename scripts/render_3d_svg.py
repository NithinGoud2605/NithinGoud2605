#!/usr/bin/env python3
"""Render data/contributions.json as an isometric 3D calendar (assets/contrib-3d-{dark,light}.svg).

One tower per day: height by contribution level, GitHub's green scale on top, darker shades on the
two visible sides. Towers grow in week by week.
"""
import json

from theme import ROOT, THEMES, prompt, window, write

W, H = 860, 440
X0, OY = 22, 352          # projection origin
DX, RX = 14.0, 9.2        # x step per week / per weekday
DY, RY = 4.35, 7.9        # y step per week (up) / per weekday (down)
GAP = 0.12                # inset per tile so towers read as separate blocks


def p(c, r):
    return X0 + c * DX + r * RX, OY - c * DY + r * RY


def shade(hex_color, f):
    n = int(hex_color[1:], 16)
    return "#%02x%02x%02x" % (int((n >> 16) * f), int((n >> 8 & 255) * f), int((n & 255) * f))


def poly(points, fill):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" fill="{fill}"/>'


def render(t, data):
    weeks = data["weeks"][-53:]
    cells = [(c, r, d["level"]) for c, wk in enumerate(weeks) for r, d in enumerate(wk)]
    # Painter's order: back (high week, low weekday) to front.
    cells.sort(key=lambda x: x[1] * RY - x[0] * DY)

    towers = []
    for c, r, lvl in cells:
        h = lvl * 14 + 4 if lvl else 2
        top = t["heat"][lvl]
        a, b, cc, d = p(c + GAP, r + GAP), p(c + 1 - GAP, r + GAP), p(c + 1 - GAP, r + 1 - GAP), p(c + GAP, r + 1 - GAP)
        up = lambda q: (q[0], q[1] - h)
        faces = (poly([d, cc, up(cc), up(d)], shade(top, 0.55))
                 + poly([b, cc, up(cc), up(b)], shade(top, 0.75))
                 + poly([up(a), up(b), up(cc), up(d)], top))
        towers.append(f'<g class="t w{c}">{faces}</g>')

    delays = "".join(f".w{i}{{animation-delay:{0.5 + i * 0.03:.2f}s}}" for i in range(len(weeks)))
    css = (".t{opacity:0;transform-box:fill-box;transform-origin:50% 100%;animation:grow .5s ease-out forwards}"
           "@keyframes grow{from{opacity:0;transform:scaleY(0)}to{opacity:1;transform:scaleY(1)}}"
           ".late{opacity:0;animation:fade .5s ease-out 2.4s forwards}"
           "@media (prefers-reduced-motion:reduce){.t,.late{animation:none;opacity:1}}" + delays)
    stats = (f'<text x="{W - 22}" y="{H - 18}" text-anchor="end" class="dim late" style="font-size:12px">'
             f'<tspan class="g bold">{data["total"]:,}</tspan> contributions · current streak '
             f'<tspan class="g bold">{data["current_streak"]}d</tspan> · longest streak '
             f'<tspan class="g bold">{data["longest_streak"]}d</tspan></text>')
    body = f'{prompt(t, 22, 44, "gh contributions --3d")}\n{"".join(towers)}\n{stats}'
    return window(t, W, H, "~/contributions — last 12 months", body, css, f'{data["total"]} contributions in the last year')


def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    for name, t in THEMES.items():
        write("contrib-3d", name, render(t, data))
    print("Wrote contrib-3d-{dark,light}.svg")


if __name__ == "__main__":
    main()
