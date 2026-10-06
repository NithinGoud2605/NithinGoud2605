#!/usr/bin/env python3
"""Render the neofetch-style info card (info-card.svg). Reads live stats from data/contributions.json."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Must match the portrait height (make_ascii_svg.py) so the two sit flush side by side.
W, H = 490, 420
LINE = 21

ROWS = [
    ("Name", "Sai Nithin Goud Kurremula"),
    ("Role", "Engineer"),
    ("Languages", "Python, TypeScript, JavaScript, SQL"),
    ("Frontend", "React, HTML, CSS"),
    ("Backend", "Django, Node, REST APIs"),
    ("Cloud", "AWS (EC2, S3, Lambda)"),
    ("Tools", "Git, Docker, GitHub Actions"),
    ("Focus", "Scalable services, AI-powered apps"),
    None,
    ("Web", "sainithingoud.vercel.app"),
    ("LinkedIn", "in/sainithingoudk"),
    ("Email", "sainithingoudk@gmail.com"),
]

BLOCKS = ["#484f58", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]


def main():
    stats_path = ROOT / "data" / "contributions.json"
    rows = list(ROWS)
    if stats_path.exists():
        s = json.loads(stats_path.read_text())
        rows[9:9] = [("Contribs", f"{s['total']:,} in the last year"),
                     ("Streak", f"{s['current_streak']}d current, {s['longest_streak']}d longest"),
                     None]

    x0, y = 22, 82
    lines, i = [], 0
    for row in rows:
        if row is None:
            y += LINE // 2
            continue
        key, value = row
        lines.append(
            f'<text class="r" style="animation-delay:{0.5 + i * 0.12:.2f}s" x="{x0}" y="{y}">'
            f'<tspan class="k">{escape(key)}</tspan><tspan x="{x0 + 104}">{escape(value)}</tspan></text>'
        )
        y += LINE
        i += 1
    blocks = "".join(
        f'<rect class="r" style="animation-delay:{0.5 + i * 0.12:.2f}s" x="{x0 + n * 24}" y="{y - 4}" width="20" height="14" rx="2" fill="{c}"/>'
        for n, c in enumerate(BLOCKS)
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Sai Nithin Goud Kurremula, Engineer">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;fill:#c9d1d9}}
.k{{fill:#39d353;font-weight:700}} .t{{fill:#58a6ff;font-weight:700;font-size:15px}} .dim{{fill:#8b949e}}
.r{{opacity:0;animation:in .4s ease-out forwards}}
@keyframes in{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
.cur{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/><circle cx="50" cy="16" r="5" fill="#27c93f"/>
<text class="dim" x="{W / 2}" y="20" text-anchor="middle" font-size="11">~/ — neofetch</text>
<text class="t" x="{x0}" y="50">nithin<tspan class="dim">@</tspan>github</text>
<text class="dim" x="{x0}" y="64">{"─" * 30}</text>
{"".join(lines)}
{blocks}
<rect class="cur" x="{x0}" y="{H - 24}" width="8" height="14" fill="#39d353"/>
</svg>
'''
    (ROOT / "info-card.svg").write_text(svg, encoding="utf-8")
    print(f"Wrote info-card.svg (last row at y={y})")


if __name__ == "__main__":
    main()
