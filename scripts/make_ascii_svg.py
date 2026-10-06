#!/usr/bin/env python3
"""Turn source-photo.png into a coloured, self-typing ASCII portrait (assets/ascii-portrait-{dark,light}.svg).

Run locally once (needs Pillow + numpy); the result is committed. The source art already has a
transparent background, so its alpha channel is the mask and no background removal is needed.
"""
import numpy as np
from PIL import Image, ImageEnhance

from theme import ROOT, THEMES, window, write

W, H = 370, 420                 # info card height must match H
AX, AY, AW, AH = 8, 34, 354, 378  # ASCII area inside the terminal frame
COLS, ROWS = 72, 46
CW, CH = AW / COLS, AH / ROWS
RAMP = " .:-=+*o#%@"            # dim -> dense (drawn light-on-dark)

# source-photo.png is already cropped to head and shoulders; its aspect matches AW:AH.


def main():
    for name, t in THEMES.items():
        svg = render(name, t)
        write("ascii-portrait", name, svg)
        print(f"Wrote ascii-portrait-{name}.svg ({len(svg) // 1024} KB)")


def render(name, t):
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
                # Dark theme: lift towards white so dark tones stay visible on the near-black panel.
                # Light theme: darken so pale skin tones stay readable on white. Then quantise to #rgb.
                boosted = 45 + rgb[r, c] * (210 / 255) if name == "dark" else rgb[r, c] * 0.72
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

    body = (f'<defs><clipPath id="reveal">{"".join(clips)}</clipPath></defs>'
            f'<g class="a" clip-path="url(#reveal)" xml:space="preserve">{"".join(rows_svg)}</g>')
    return window(t, W, H, "~/ — portrait.txt", body, ".a text{font-size:8.3px;white-space:pre}", "ASCII portrait of Nithin")


if __name__ == "__main__":
    main()
