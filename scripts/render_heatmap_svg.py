#!/usr/bin/env python3
"""Render data/contributions.json as an animated heatmap panel (assets/contrib-heatmap-{dark,light}.svg)."""
import json
from collections import Counter
from datetime import date

from theme import ROOT, THEMES, prompt, window, write

W, H = 860, 226
CELL, GAP = 12, 3
STEP = CELL + GAP
LEFT, TOP = 46, 66
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def render(t, data):
    weeks = data["weeks"][-53:]
    days = [d for wk in weeks for d in wk]
    busiest = max(days, key=lambda d: d["count"])
    per_month = Counter()
    for d in days:
        per_month[d["date"][:7]] += d["count"]
    top_month, top_month_n = per_month.most_common(1)[0]
    bd = date.fromisoformat(busiest["date"])
    tm = date.fromisoformat(top_month + "-01")

    cells, month_labels, last_month = [], [], None
    for wi, week in enumerate(weeks):
        first = date.fromisoformat(week[0]["date"])
        if first.month != last_month and first.day <= 7:
            month_labels.append(f'<text class="dim" style="font-size:10px" x="{LEFT + wi * STEP}" y="{TOP - 8}">{MONTHS[first.month - 1]}</text>')
            last_month = first.month
        for d in week:
            dow = (date.fromisoformat(d["date"]).weekday() + 1) % 7  # Sunday first, like GitHub
            title = f'{d["count"]} contribution{"" if d["count"] == 1 else "s"} on {d["date"]}'
            cells.append(
                f'<rect class="c w{wi}" x="{LEFT + wi * STEP}" y="{TOP + dow * STEP}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{t["heat"][d["level"]]}"><title>{title}</title></rect>'
            )

    delays = "".join(f".w{i}{{animation-delay:{0.6 + i * 0.035:.3f}s}}" for i in range(len(weeks)))
    css = (
        ".c{opacity:0;animation:pop .35s ease-out forwards;transform-box:fill-box;transform-origin:center}"
        "@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:scale(1)}}"
        ".type{clip-path:inset(0 100% 0 0);animation:type .6s steps(30,end) .1s forwards}"
        "@keyframes type{to{clip-path:inset(0 0 0 0)}}"
        ".late{opacity:0;animation:fade .5s ease-out 2.6s forwards}"
        "@media (prefers-reduced-motion:reduce){.c,.late{animation:none;opacity:1}.type{animation:none;clip-path:none}}" + delays
    )
    legend_x = W - 24 - 5 * STEP - 74
    legend = "".join(
        f'<rect x="{legend_x + 34 + i * STEP}" y="{H - 42}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>'
        for i, c in enumerate(t["heat"])
    )
    body = f'''<g class="type">{prompt(t, 18, 44, f"gh contributions --user {data['username']}")}</g>
{"".join(month_labels)}
<text class="dim" style="font-size:9px" x="{LEFT - 8}" y="{TOP + 1 * STEP + 9}" text-anchor="end">Mon</text>
<text class="dim" style="font-size:9px" x="{LEFT - 8}" y="{TOP + 3 * STEP + 9}" text-anchor="end">Wed</text>
<text class="dim" style="font-size:9px" x="{LEFT - 8}" y="{TOP + 5 * STEP + 9}" text-anchor="end">Fri</text>
{"".join(cells)}
<g class="late">
<text x="18" y="{H - 32}" class="dim" style="font-size:12px"><tspan class="g bold">{data["total"]:,}</tspan> contributions · current streak <tspan class="g bold">{data["current_streak"]}d</tspan> · longest <tspan class="g bold">{data["longest_streak"]}d</tspan></text>
<text x="18" y="{H - 14}" class="dim" style="font-size:12px">busiest day <tspan class="o bold">{busiest["count"]}</tspan> on {MONTHS[bd.month - 1]} {bd.day} · busiest month <tspan class="o bold">{MONTHS[tm.month - 1]} {tm.year}</tspan> ({top_month_n:,})</text>
<text class="dim" style="font-size:11px" x="{legend_x}" y="{H - 32}">Less</text>{legend}<text class="dim" style="font-size:11px" x="{legend_x + 34 + 5 * STEP + 4}" y="{H - 32}">More</text>
</g>'''
    return window(t, W, H, "~/contributions — last 12 months", body, css, f'{data["total"]} contributions in the last year')


def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    for name, t in THEMES.items():
        write("contrib-heatmap", name, render(t, data))
    print("Wrote contrib-heatmap-{dark,light}.svg")


if __name__ == "__main__":
    main()
