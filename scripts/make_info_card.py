#!/usr/bin/env python3
"""Render the neofetch-style info card (assets/info-card-{dark,light}.svg) with live stats."""
import json
from html import escape

from theme import ROOT, THEMES, fade, write, window

# Must match the portrait height (make_ascii_svg.py) so the two sit flush side by side.
W, H = 490, 420
LINE = 21

ROWS = [
    ("Name", "Sai Nithin Goud Kurremula"),
    ("Role", "Engineer"),
    ("Location", "San Francisco"),
    ("Languages", "Python, TypeScript, JavaScript, SQL"),
    ("Frontend", "React, Vite, Tailwind"),
    ("Backend", "Node, Express, Django, Flask"),
    ("Data", "Postgres, Supabase, Redis"),
    ("Cloud", "AWS, Cloudflare Workers, Vercel"),
    ("AI", "LLM agents, LangChain, OpenAI"),
    None,
    ("Web", "sainithingoud.vercel.app"),
]

BLOCK_KEYS = ["dim", "red", "green", "orange", "blue", "purple", "fg"]


def render(t, stats):
    rows = list(ROWS)
    if stats:
        rows[10:10] = [("Contribs", f"{stats['total']:,} in the last year"),
                       ("Streak", f"{stats['current_streak']}d current, {stats['longest_streak']}d longest"),
                       None]
    x0, y = 22, 82
    lines, i = [], 0
    for row in rows:
        if row is None:
            y += LINE // 2
            continue
        key, value = row
        lines.append(f'<text class="fade" {fade(i)} x="{x0}" y="{y}"><tspan class="g bold">{escape(key)}</tspan>'
                     f'<tspan x="{x0 + 104}">{escape(value)}</tspan></text>')
        y += LINE
        i += 1
    blocks = "".join(
        f'<rect class="fade" {fade(i)} x="{x0 + n * 24}" y="{y - 4}" width="20" height="14" rx="2" fill="{t[k]}"/>'
        for n, k in enumerate(BLOCK_KEYS)
    )
    body = f'''<text x="{x0}" y="50" class="b bold" style="font-size:15px">nithin<tspan class="dim">@</tspan>github</text>
<text class="dim" x="{x0}" y="64">{"─" * 30}</text>
{"".join(lines)}
{blocks}
<rect class="cur" x="{x0}" y="{H - 24}" width="8" height="14" fill="{t['green']}"/>'''
    return window(t, W, H, "~/ — neofetch", body, label="Sai Nithin Goud Kurremula, Engineer")


def main():
    path = ROOT / "data" / "contributions.json"
    stats = json.loads(path.read_text()) if path.exists() else None
    for name, t in THEMES.items():
        write("info-card", name, render(t, stats))
    print("Wrote info-card-{dark,light}.svg")


if __name__ == "__main__":
    main()
