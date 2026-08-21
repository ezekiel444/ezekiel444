#!/usr/bin/env python3
"""
Generate a profile card SVG: ASCII portrait left, all info right.
One unified block, tight spacing, large readable text.

Usage:
    python3 scripts/generate_profile_card.py

Output:
    image/profile_card.svg
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


# Config
INPUT_IMAGE = "image/eml.jpg"
OUTPUT_SVG = "image/profile_card.svg"
PORTRAIT_WIDTH = 150
FONT_SIZE = 4  # smaller chars = more detail in face
INFO_FONT_SIZE = 13
BG_COLOR = "#0D1117"
CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

# All info lines — one continuous block on the right
INFO_LINES = [
    ("title", "matomi@cloud"),
    ("separator", ""),
    ("label_value", ("Role:", "DevOps Engineer")),
    ("label_value", ("Cloud:", "Azure, AWS, GCP")),
    ("label_value", ("Host:", "South Africa")),
    ("label_value", ("Uptime:", "5+ years")),
    ("label_value", ("IDE:", "VS Code")),
    ("spacer", ""),
    ("header", "Stack"),
    ("label_value", ("Infra:", "Kubernetes, Docker, Terraform")),
    ("label_value", ("IaC:", "Ansible, Helm, Pulumi")),
    ("label_value", ("CI/CD:", "GitLab CI, GitHub Actions")),
    ("label_value", ("Monitor:", "Prometheus, Grafana, ELK")),
    ("label_value", ("Dev:", "React, Next.js, Node.js")),
    ("label_value", ("Lang:", "Python, Bash, TypeScript")),
    ("spacer", ""),
    ("header", "Contact"),
    ("label_value", ("Web:", "ezekielmatomilucky.com")),
    ("label_value", ("GitHub:", "@ezekiel444")),
    ("spacer", ""),
    ("header", "Status"),
    ("label_value", ("Now:", "Open to work")),
    ("label_value", ("Focus:", "Cloud Architecture & DevOps")),
]

# Colors
COLORS = {
    "title": "#5B7D99",
    "separator": "#2C4A5E",
    "label": "#D4AF37",
    "value": "#E8DCC8",
    "header": "#D4AF37",
}


def load_and_resize(path: str, width: int):
    img = Image.open(path)
    w, h = img.size
    aspect = h / w
    new_height = int(aspect * width * 0.55)
    img = img.resize((width, new_height), Image.LANCZOS)
    return img


def generate_portrait_rows(image, chars):
    width, height = image.size
    color_img = image.convert("RGB")
    gray_img = image.convert("L")
    color_pixels = list(color_img.getdata())
    gray_pixels = list(gray_img.getdata())
    num_chars = len(chars)

    rows = []
    for row in range(height):
        spans = []
        prev_color = None
        current_run = ""
        for col in range(width):
            idx = row * width + col
            brightness = gray_pixels[idx]
            char_idx = brightness * (num_chars - 1) // 255
            char = chars[char_idx]
            r, g, b = color_pixels[idx]
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            if hex_color == prev_color:
                current_run += escape(char)
            else:
                if current_run:
                    spans.append((prev_color, current_run))
                current_run = escape(char)
                prev_color = hex_color
        if current_run:
            spans.append((prev_color, current_run))
        rows.append(spans)
    return rows, height


def build_info_line(line_type, data, x, y):
    fs = INFO_FONT_SIZE
    ff = 'font-family="monospace"'
    if line_type == "title":
        return (f'<text x="{x}" y="{y}" fill="{COLORS["title"]}" '
                f'font-weight="bold" font-size="{fs + 5}px" {ff}>{escape(data)}</text>')
    elif line_type == "separator":
        return (f'<text x="{x}" y="{y}" fill="{COLORS["separator"]}" '
                f'font-size="{fs}px" {ff}>{"═" * 38}</text>')
    elif line_type == "label_value":
        label, value = data
        return (f'<text x="{x}" y="{y}" font-size="{fs}px" {ff}>'
                f'<tspan fill="{COLORS["label"]}" font-weight="bold">{escape(label)}</tspan>'
                f'<tspan fill="{COLORS["value"]}"> {escape(value)}</tspan></text>')
    elif line_type == "header":
        return (f'<text x="{x}" y="{y}" font-size="{fs}px" {ff}>'
                f'<tspan fill="{COLORS["separator"]}">── </tspan>'
                f'<tspan fill="{COLORS["header"]}" font-weight="bold">{escape(data)}</tspan>'
                f'<tspan fill="{COLORS["separator"]}"> {"─" * (24 - len(data))}</tspan></text>')
    elif line_type == "spacer":
        return ""
    return ""


def generate_profile_card():
    print(f"Loading: {INPUT_IMAGE}")

    image = load_and_resize(INPUT_IMAGE, PORTRAIT_WIDTH)
    portrait_rows, portrait_height = generate_portrait_rows(image, CHARS)

    char_w = FONT_SIZE * 0.6
    char_h = FONT_SIZE * 1.2

    # Measurements
    pad = 15
    portrait_px_w = int(PORTRAIT_WIDTH * char_w)
    portrait_px_h = int(portrait_height * char_h)
    gap = 25  # tight gap between portrait and text

    # Info line height — tight but readable
    info_lh = INFO_FONT_SIZE * 1.7

    # Total info height
    info_total_h = len(INFO_LINES) * info_lh

    # Card dimensions — height is max of portrait or info
    card_height = int(max(portrait_px_h, info_total_h) + pad * 2)
    info_panel_w = 420
    card_width = pad + portrait_px_w + gap + info_panel_w + pad

    # Vertical centering
    portrait_y0 = (card_height - portrait_px_h) / 2
    info_y0 = (card_height - info_total_h) / 2

    info_x = pad + portrait_px_w + gap

    # Build SVG
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {card_width} {card_height}" '
               f'width="{card_width}" height="{card_height}">')

    # Background
    svg.append(f'  <rect width="100%" height="100%" fill="{BG_COLOR}" rx="6"/>')

    # Subtle border
    svg.append(f'  <rect width="100%" height="100%" rx="6" '
               f'fill="none" stroke="#2C4A5E" stroke-width="0.5" opacity="0.4"/>')

    # Portrait
    for i, spans in enumerate(portrait_rows):
        y = portrait_y0 + (i + 1) * char_h
        tspans = ''.join(f'<tspan fill="{c}">{t}</tspan>' for c, t in spans)
        svg.append(f'  <text x="{pad}" y="{y:.1f}" '
                   f'font-family="monospace" font-size="{FONT_SIZE}px" '
                   f'xml:space="preserve">{tspans}</text>')

    # Info lines
    for i, (lt, data) in enumerate(INFO_LINES):
        y = info_y0 + (i + 1) * info_lh
        line = build_info_line(lt, data, info_x, y)
        if line:
            svg.append(f'  {line}')

    svg.append('</svg>')

    output = "\n".join(svg)
    Path(OUTPUT_SVG).parent.mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_SVG).write_text(output, encoding="utf-8")
    print(f"Card: {card_width}x{card_height}px")
    print(f"Portrait: {portrait_px_w}x{portrait_px_h}px | Info: {len(INFO_LINES)} lines at {INFO_FONT_SIZE}px")


if __name__ == "__main__":
    generate_profile_card()
