#!/usr/bin/env python3
"""
Generate a combined profile card SVG: ASCII portrait on the left,
developer info panel on the right. One unified image for the README.

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
PORTRAIT_WIDTH = 80  # chars for portrait (left side)
FONT_SIZE = 7
INFO_FONT_SIZE = 16  # big, readable font for info panel
BG_COLOR = "#0D1117"
CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

# Info panel content — edit these to update your profile
INFO_LINES = [
    ("title", "matomi@cloud"),
    ("separator", ""),
    ("label_value", ("Role:", "DevOps Engineer")),
    ("label_value", ("Cloud:", "Azure, AWS, GCP")),
    ("label_value", ("Host:", "South Africa")),
    ("label_value", ("Uptime:", "5+ years")),
    ("spacer", ""),
    ("header", "Stack"),
    ("label_value", ("Infra:", "K8s, Docker, Terraform")),
    ("label_value", ("CI/CD:", "GitLab CI, GitHub Actions")),
    ("label_value", ("Monitor:", "Prometheus, Grafana")),
    ("label_value", ("Dev:", "React, Next.js, Node.js")),
    ("label_value", ("Lang:", "Python, Bash, TypeScript")),
    ("spacer", ""),
    ("header", "Contact"),
    ("label_value", ("Web:", "ezekielmatomilucky.com")),
    ("label_value", ("GitHub:", "@ezekiel444")),
    ("spacer", ""),
    ("header", "Status"),
    ("label_value", ("Now:", "Open to work")),
]

# Color scheme
COLORS = {
    "title": "#5B7D99",
    "separator": "#2C4A5E",
    "label": "#D4AF37",
    "value": "#E8DCC8",
    "section": "#5B7D99",
    "header": "#D4AF37",
}


def load_and_resize(path: str, width: int):
    """Load image and resize for ASCII conversion."""
    img = Image.open(path)
    w, h = img.size
    aspect = h / w
    new_height = int(aspect * width * 0.55)
    img = img.resize((width, new_height), Image.LANCZOS)
    return img


def generate_portrait_rows(image, chars):
    """Generate colored ASCII rows from image."""
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


def build_info_line_svg(line_type, data, x_start, y_pos, font_size):
    """Build SVG text element for an info line."""
    fs = INFO_FONT_SIZE

    if line_type == "title":
        return (f'<text x="{x_start}" y="{y_pos}" '
                f'fill="{COLORS["title"]}" font-weight="bold" '
                f'font-size="{fs + 6}px">{escape(data)}</text>')

    elif line_type == "separator":
        sep = "═" * 32
        return (f'<text x="{x_start}" y="{y_pos}" '
                f'fill="{COLORS["separator"]}" '
                f'font-size="{fs}px">{sep}</text>')

    elif line_type == "label_value":
        label, value = data
        return (f'<text x="{x_start}" y="{y_pos}" font-size="{fs}px">'
                f'<tspan fill="{COLORS["label"]}">{escape(label)}</tspan>'
                f'<tspan fill="{COLORS["value"]}">  {escape(value)}</tspan>'
                f'</text>')

    elif line_type == "section":
        return (f'<text x="{x_start}" y="{y_pos}" '
                f'fill="{COLORS["section"]}" font-weight="bold" '
                f'font-size="{fs}px">{escape(data)}</text>')

    elif line_type == "value":
        return (f'<text x="{x_start + 12}" y="{y_pos}" '
                f'fill="{COLORS["value"]}" '
                f'font-size="{fs}px">{escape(data)}</text>')

    elif line_type == "header":
        prefix = "── "
        suffix = " " + "─" * (22 - len(data))
        return (f'<text x="{x_start}" y="{y_pos}" font-size="{fs}px">'
                f'<tspan fill="{COLORS["separator"]}">{prefix}</tspan>'
                f'<tspan fill="{COLORS["header"]}" font-weight="bold">{escape(data)}</tspan>'
                f'<tspan fill="{COLORS["separator"]}">{suffix}</tspan>'
                f'</text>')

    elif line_type == "spacer":
        return ""

    return ""


def generate_profile_card():
    """Generate the full profile card SVG."""
    print(f"Loading: {INPUT_IMAGE}")

    image = load_and_resize(INPUT_IMAGE, PORTRAIT_WIDTH)
    portrait_rows, portrait_height = generate_portrait_rows(image, CHARS)

    char_w = FONT_SIZE * 0.6
    char_h = FONT_SIZE * 1.2

    # Dimensions
    portrait_pixel_width = int(PORTRAIT_WIDTH * char_w)
    gap = 40  # space between portrait and info
    info_panel_width = 500
    total_width = portrait_pixel_width + gap + info_panel_width + 20
    total_height = int(portrait_height * char_h) + 20

    # Make sure info fits vertically
    info_line_height = INFO_FONT_SIZE * 2.0
    min_height_for_info = len(INFO_LINES) * info_line_height + 50
    total_height = max(total_height, int(min_height_for_info))

    info_x = portrait_pixel_width + gap
    info_y_start = 30

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {total_width} {total_height}" '
               f'width="{total_width}" height="{total_height}">')

    # Defs
    svg.append('  <defs>')
    svg.append('    <linearGradient id="shimmer" x1="0%" y1="0%" x2="100%" y2="0%">')
    svg.append('      <stop offset="0%" style="stop-color:rgba(255,255,255,0);"/>')
    svg.append('      <stop offset="45%" style="stop-color:rgba(255,255,255,0);"/>')
    svg.append('      <stop offset="50%" style="stop-color:rgba(255,255,255,0.06);"/>')
    svg.append('      <stop offset="55%" style="stop-color:rgba(255,255,255,0);"/>')
    svg.append('      <stop offset="100%" style="stop-color:rgba(255,255,255,0);"/>')
    svg.append('      <animate attributeName="x1" values="-100%;100%" dur="5s" repeatCount="indefinite"/>')
    svg.append('      <animate attributeName="x2" values="0%;200%" dur="5s" repeatCount="indefinite"/>')
    svg.append('    </linearGradient>')
    svg.append('  </defs>')

    # Background
    svg.append(f'  <rect width="100%" height="100%" fill="{BG_COLOR}" rx="6" ry="6"/>')

    # Styles
    svg.append('  <style>')
    svg.append('    text {')
    svg.append('      font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace;')
    svg.append(f'      font-size: {FONT_SIZE}px;')
    svg.append('      white-space: pre;')
    svg.append('    }')
    svg.append('    .row { opacity: 0; animation: reveal 0.02s ease-in forwards; }')
    svg.append('    @keyframes reveal { from { opacity: 0; } to { opacity: 1; } }')
    svg.append('    .card { animation: breathe 6s ease-in-out infinite; }')
    svg.append('    @keyframes breathe {')
    svg.append('      0%, 100% { opacity: 1; filter: brightness(1); }')
    svg.append('      50% { opacity: 0.97; filter: brightness(1.02); }')
    svg.append('    }')
    svg.append('    .info-line { opacity: 0; animation: fadeIn 0.3s ease-in forwards; }')
    svg.append('    @keyframes fadeIn { from { opacity: 0; transform: translateX(5px); } to { opacity: 1; transform: translateX(0); } }')
    svg.append('  </style>')

    svg.append('  <g class="card">')

    # Portrait rows
    for row_idx, spans in enumerate(portrait_rows):
        y_pos = 10 + (row_idx + 1) * char_h
        delay = row_idx * 0.03
        tspans = ''.join(f'<tspan fill="{color}">{text}</tspan>' for color, text in spans)
        svg.append(
            f'  <text class="row" x="10" y="{y_pos:.1f}" '
            f'style="animation-delay:{delay:.2f}s">{tspans}</text>'
        )

    # Info panel
    info_start_delay = 0.5  # start after portrait begins revealing
    for i, (line_type, data) in enumerate(INFO_LINES):
        y_pos = info_y_start + i * info_line_height
        delay = info_start_delay + i * 0.06
        line_svg = build_info_line_svg(line_type, data, info_x, y_pos, FONT_SIZE)
        if line_svg:
            # Wrap in group for animation
            svg.append(
                f'  <g class="info-line" style="animation-delay:{delay:.2f}s">'
                f'{line_svg}</g>'
            )

    svg.append('  </g>')

    # Shimmer overlay
    svg.append(f'  <rect width="{portrait_pixel_width}" height="100%" '
               f'fill="url(#shimmer)" style="mix-blend-mode:overlay;pointer-events:none;"/>')

    # Subtle border
    svg.append(f'  <rect width="100%" height="100%" rx="6" ry="6" '
               f'fill="none" stroke="#2C4A5E" stroke-width="1" opacity="0.5"/>')

    svg.append('</svg>')

    # Write
    output = "\n".join(svg)
    Path(OUTPUT_SVG).parent.mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_SVG).write_text(output, encoding="utf-8")
    print(f"Generated: {OUTPUT_SVG}")
    print(f"Dimensions: {total_width}x{total_height}px")
    print(f"Portrait: {PORTRAIT_WIDTH} chars, Info: {len(INFO_LINES)} lines")


if __name__ == "__main__":
    generate_profile_card()
