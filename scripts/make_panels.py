#!/usr/bin/env python3
"""Render the static panels: typing header, now.md, career timeline, contact buttons, footer.

Content lives in the constants below; edit them and rerun (the daily workflow reruns this too).
"""
from html import escape

from theme import THEMES, fade, prompt, window, write

FULL = 860

HEADER_LINES = [
    "Hi, I'm Sai Nithin Goud.",
    "I build products from 0 to 1.",
    "Backend, real-time data, AI features.",
    "React on top, Postgres underneath.",
]
TAGLINE = "Engineer · full-stack products, real-time systems and AI workflows · San Francisco"

NOW = [
    ("h", "# Now"),
    ("", "→ Building an AI-enabled marketplace,"),
    ("", "  end to end, as an early engineer"),
    ("", "→ Real-time sync with WebSockets + Redis"),
    ("", "→ AI-assisted workflows in the product"),
    ("", "→ Side projects: Finorn, Savebucks"),
    ("gap", ""),
    ("h", "# Daily stack"),
    ("", "→ TypeScript, React, Postgres, Supabase"),
]
NOW_UPDATED = "updated Oct 2026"

# (year, title, where · when, is_current)
CAREER = [
    ("2026", "Founding Engineer", "Anthum · San Francisco · Feb 2026 – now", True),
    ("2025", "Software Developer Intern", "Nuubi · Remote · Oct 2025 – Jan 2026", False),
    ("2024", "M.S. Computer Science", "University of Cincinnati · 2024 – 2026", False),
    ("2024", "Software Engineer", "Skyinfolab Software Solutions · Jan – Aug 2024", False),
    ("2020", "B.S. Computer Science & Game Dev", "Backstage Pass Institute · 2020 – 2024", False),
]

BUTTONS = [("portfolio", "sainithingoud.vercel.app"), ("linkedin", "in/sainithingoudk"), ("email", "sainithingoudk@gmail.com")]

SIDE_H = 300  # now.md (370) and timeline (490) sit side by side at this height


def header(t):
    w, h, x0, y = FULL, 132, 22, 90
    size, cw = 24, 14.45  # monospace advance is ~0.6em
    n, slot = len(HEADER_LINES), 3.4
    total = n * slot
    clips, texts, cursor_x = [], [], []
    for i, line in enumerate(HEADER_LINES):
        width = len(line) * cw + 4
        a, b, c, d = i / n, (i + 0.38) / n, (i + 0.82) / n, (i + 0.96) / n
        keys = [0, a or 0.0001, b, c, d, 1]  # keyTimes must not repeat 0 for the first line
        kt = ";".join(f"{k:.4f}" for k in keys)
        clips.append(f'<clipPath id="l{i}"><rect x="{x0}" y="{y - 26}" height="34" width="0">'
                     f'<animate attributeName="width" values="0;0;{width:.0f};{width:.0f};0;0" keyTimes="{kt}" dur="{total}s" repeatCount="indefinite"/></rect></clipPath>')
        texts.append(f'<text clip-path="url(#l{i})" x="{x0}" y="{y}" class="br bold" style="font-size:{size}px">{escape(line)}</text>')
        cursor_x.append((keys, width))
    # One cursor that follows whichever line is typing.
    vals, kts = [], []
    for i, (keys, width) in enumerate(cursor_x):
        for k, v in zip(keys[1:5], [0, width, width, 0]):
            kts.append(k)
            vals.append(x0 + v)
    kts = [0] + kts + [1]
    vals = [x0] + vals + [x0]
    cursor = (f'<rect class="cur" x="{x0}" y="{y - 21}" width="12" height="26" fill="{t["green"]}">'
              f'<animate attributeName="x" values="{";".join(f"{v:.0f}" for v in vals)}" keyTimes="{";".join(f"{k:.4f}" for k in kts)}" dur="{total}s" repeatCount="indefinite"/></rect>')
    body = f'''<defs>{"".join(clips)}</defs>
{prompt(t, x0, 48, "whoami")}
{"".join(texts)}
{cursor}
<text x="{x0}" y="{h - 16}" class="dim fade" {fade(0, 0.6)}>{escape(TAGLINE)}</text>'''
    return window(t, w, h, "~/ — zsh", body, label=HEADER_LINES[0] + " " + TAGLINE)


def now(t):
    w, x0 = 370, 22
    lines, y, i = [], 80, 0
    for kind, text in NOW:
        if kind == "gap":
            y += 10
            continue
        cls = "b bold" if kind == "h" else ""
        lines.append(f'<text x="{x0}" y="{y}" class="fade {cls}" {fade(i)} xml:space="preserve">{escape(text)}</text>')
        y += 21
        i += 1
    body = f'''{prompt(t, x0, 48, "cat now.md")}
{"".join(lines)}
<g class="fade" {fade(i)}><text x="{x0}" y="{SIDE_H - 18}" class="dim" style="font-size:11px">{escape(NOW_UPDATED)}</text></g>'''
    return window(t, w, SIDE_H, "~/ — now.md", body, label="What I'm working on now")


def timeline(t):
    w, x0, gx = 490, 22, 30
    items, y = [], 84
    for i, (year, title, where, current) in enumerate(CAREER):
        head = (f'<tspan class="o">{year}</tspan>  <tspan class="br bold">{escape(title)}</tspan>'
                + (' <tspan class="g">(HEAD)</tspan>' if current else ""))
        items.append(f'''<g class="fade" {fade(i)}>
<circle cx="{gx}" cy="{y - 4}" r="5" fill="{t['bg']}" stroke="{t['green'] if current else t['dim']}" stroke-width="2"/>
<text x="{gx + 16}" y="{y}">{head}</text>
<text x="{gx + 16 + 48}" y="{y + 18}" class="dim" style="font-size:12px">{escape(where)}</text></g>''')
        y += 42
    body = f'''{prompt(t, x0, 48, "git log --graph career")}
<line x1="{gx}" x2="{gx}" y1="80" y2="{84 + (len(CAREER) - 1) * 42}" stroke="{t['border']}" stroke-width="2"/>
{"".join(items)}'''
    return window(t, w, SIDE_H, "~/ — career", body, label="Career timeline")


def button(t, name, value):
    w, h = 270, 44
    body = (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="8" fill="{t["bg"]}" stroke="{t["border"]}"/>'
            f'<text x="16" y="27"><tspan class="g bold">→</tspan> <tspan class="br bold">{name}</tspan> <tspan class="dim" style="font-size:11px">{escape(value)}</tspan></text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{name}: {escape(value)}">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;fill:{t["fg"]}}}.g{{fill:{t["green"]}}}.br{{fill:{t["bright"]}}}.dim{{fill:{t["dim"]}}}.bold{{font-weight:700}}</style>
{body}
</svg>
'''


def footer(t):
    w, h, x0 = FULL, 64, 22
    body = f'''<text x="{x0}" y="46"><tspan class="g">nithin@github</tspan><tspan class="dim"> ~ $ </tspan><tspan class="br">exit</tspan><tspan class="dim"> · logout · thanks for stopping by</tspan></text>
<rect class="cur" x="{w - 40}" y="34" width="9" height="15" fill="{t['green']}"/>'''
    return window(t, w, h, "", body, label="Thanks for visiting")


def main():
    for name, t in THEMES.items():
        write("header", name, header(t))
        write("now", name, now(t))
        write("timeline", name, timeline(t))
        write("footer", name, footer(t))
        for b, v in BUTTONS:
            write(f"btn-{b}", name, button(t, b, v))
    print("Wrote header, now, timeline, footer and buttons (dark + light)")


if __name__ == "__main__":
    main()
