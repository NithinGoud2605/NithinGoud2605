#!/usr/bin/env python3
"""Render data/contributions.json as an animated terminal-style heatmap (contrib-heatmap.svg)."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

W, H = 860, 210
CELL, GAP = 12, 3
STEP = CELL + GAP
LEFT, TOP = 46, 66
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    weeks = data["weeks"][-53:]

    cells, month_labels = [], []
    last_month = None
    for wi, week in enumerate(weeks):
        first = date.fromisoformat(week[0]["date"])
        if first.month != last_month and first.day <= 7:
            month_labels.append(f'<text class="m" x="{LEFT + wi * STEP}" y="{TOP - 8}">{MONTHS[first.month - 1]}</text>')
            last_month = first.month
        for d in week:
            dow = (date.fromisoformat(d["date"]).weekday() + 1) % 7  # Sunday = 0, like GitHub
            title = f'{d["count"]} contribution{"" if d["count"] == 1 else "s"} on {d["date"]}'
            cells.append(
                f'<rect class="c w{wi}" x="{LEFT + wi * STEP}" y="{TOP + dow * STEP}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{PALETTE[d["level"]]}"><title>{title}</title></rect>'
            )

    # One delay rule per week column instead of an inline style per cell keeps the file small.
    delays = "".join(f".w{i}{{animation-delay:{0.6 + i * 0.035:.3f}s}}" for i in range(len(weeks)))
    legend_x = W - 24 - 5 * STEP - 74
    legend = "".join(
        f'<rect x="{legend_x + 34 + i * STEP}" y="{H - 26}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{data["total"]} contributions in the last year">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;fill:#8b949e}}
.cmd{{fill:#c9d1d9;font-size:13px}} .p{{fill:#39d353}} .hl{{fill:#39d353;font-weight:700}}
.m{{font-size:10px}} .d{{font-size:9px}}
.c{{opacity:0;animation:pop .35s ease-out forwards;transform-box:fill-box;transform-origin:center}}
@keyframes pop{{0%{{opacity:0;transform:scale(.3)}}70%{{opacity:1;transform:scale(1.15)}}100%{{opacity:1;transform:scale(1)}}}}
.type{{clip-path:inset(0 100% 0 0);animation:type .6s steps(30,end) .1s forwards}}
@keyframes type{{to{{clip-path:inset(0 0 0 0)}}}}
.fade{{opacity:0;animation:fade .5s ease-out 2.6s forwards}}
@keyframes fade{{to{{opacity:1}}}}
{delays}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/><circle cx="50" cy="16" r="5" fill="#27c93f"/>
<text x="{W / 2}" y="20" text-anchor="middle">~/contributions — last 12 months</text>
<g class="type"><text class="cmd" x="18" y="44"><tspan class="p">$</tspan> gh contributions --user {data["username"]}</text></g>
{"".join(month_labels)}
<text class="d" x="{LEFT - 8}" y="{TOP + 1 * STEP + 9}" text-anchor="end">Mon</text>
<text class="d" x="{LEFT - 8}" y="{TOP + 3 * STEP + 9}" text-anchor="end">Wed</text>
<text class="d" x="{LEFT - 8}" y="{TOP + 5 * STEP + 9}" text-anchor="end">Fri</text>
{"".join(cells)}
<g class="fade">
<text x="18" y="{H - 16}"><tspan class="hl">{data["total"]:,}</tspan> contributions · current streak <tspan class="hl">{data["current_streak"]}d</tspan> · longest <tspan class="hl">{data["longest_streak"]}d</tspan></text>
<text x="{legend_x}" y="{H - 16}">Less</text>{legend}<text x="{legend_x + 34 + 5 * STEP + 4}" y="{H - 16}">More</text>
</g>
</svg>
'''
    (ROOT / "contrib-heatmap.svg").write_text(svg, encoding="utf-8")
    print(f"Wrote contrib-heatmap.svg ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
