#!/usr/bin/env python3
"""Turn source-photo.png into a coloured, self-typing ASCII portrait (ascii-portrait.svg).

Run locally once (needs Pillow + numpy); the result is committed. The source art already has a
transparent background, so its alpha channel is the mask and no background removal is needed.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent

W, H = 370, 420                 # info card height must match H
AX, AY, AW, AH = 8, 34, 354, 378  # ASCII area inside the terminal frame
COLS, ROWS = 72, 46
CW, CH = AW / COLS, AH / ROWS
RAMP = " .:-=+*o#%@"            # dim -> dense (drawn light-on-dark)

# source-photo.png is already cropped to head and shoulders; its aspect matches AW:AH.


def main():
    img = Image.open(ROOT / "source-photo.png").convert("RGBA")
    img = ImageEnhance.Contrast(img).enhance(1.3)
    small = np.asarray(img.resize((COLS, ROWS), Image.LANCZOS)).astype(float)
    rgb, alpha = small[..., :3], small[..., 3] / 255

    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255
    # Stretch brightness across the subject only (ignoring the cut-out background), then lift the
    # shadows so the dark shirt and hair still read.
    lo, hi = np.percentile(lum[alpha > 0.5], [3, 99])
    lum = np.clip((lum - lo) / (hi - lo), 0, 1) ** 0.7

    rows_svg, clips = [], []
    for r in range(ROWS):
        spans, run_color, run_chars = [], None, ""
        for c in range(COLS):
            if alpha[r, c] < 0.35:
                ch, color = " ", run_color
            else:
                ch = RAMP[max(1, min(len(RAMP) - 1, int(lum[r, c] * len(RAMP))))]
                # Brighten towards white so dark tones stay visible on #0d1117, then quantise to #rgb.
                boosted = 45 + rgb[r, c] * (210 / 255)
                color = "#" + "".join(f"{int(v) >> 4:x}" for v in boosted)
            if color != run_color and run_chars.strip():
                spans.append((run_color, run_chars))
                run_chars = ""
            run_color = color if color else run_color
            run_chars += ch
        if run_chars.strip():
            spans.append((run_color, run_chars))
        if not spans:
            continue
        body = "".join(
            f'<tspan fill="{col}">{txt.replace("&", "&amp;").replace("<", "&lt;")}</tspan>' for col, txt in spans
        )
        y = AY + (r + 1) * CH - 2
        rows_svg.append(f'<text x="{AX}" y="{y:.1f}" textLength="{AW}" lengthAdjust="spacing">{body}</text>')
        begin = 0.3 + r * 0.06
        clips.append(
            f'<rect x="{AX}" y="{AY + r * CH:.1f}" width="0" height="{CH + 0.5:.1f}">'
            f'<animate attributeName="width" from="0" to="{AW}" begin="{begin:.2f}s" dur="0.25s" fill="freeze"/></rect>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ASCII portrait of Nithin">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:8.3px;white-space:pre}}</style>
<defs><clipPath id="reveal">{"".join(clips)}</clipPath></defs>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/><circle cx="50" cy="16" r="5" fill="#27c93f"/>
<text x="{W / 2}" y="20" text-anchor="middle" fill="#8b949e" style="font-size:11px">~/ — portrait.txt</text>
<g clip-path="url(#reveal)" xml:space="preserve">{"".join(rows_svg)}</g>
</svg>
'''
    (ROOT / "ascii-portrait.svg").write_text(svg, encoding="utf-8")
    print(f"Wrote ascii-portrait.svg ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
