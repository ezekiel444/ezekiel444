#!/usr/bin/env python3
"""
Convert an image to colored ASCII art SVG for GitHub profile README.

This script produces an SVG file where each character is colored to match
the corresponding pixel in the original image, creating a faithful
color-accurate ASCII portrait that renders natively on GitHub.

Usage:
    python3 scripts/image_to_ascii.py [--input IMAGE_PATH] [--output OUTPUT_PATH]
                                       [--width COLS] [--chars CHARSET]
                                       [--font-size SIZE] [--bg BG_COLOR]
                                       [--format FORMAT]

Defaults:
    --input      image/eml.jpg
    --output     image/ascii_portrait.svg
    --width      80
    --chars      dense
    --font-size  10
    --bg         #0D1117
    --format     svg

Examples:
    # Generate colored SVG (default)
    python3 scripts/image_to_ascii.py

    # Higher detail
    python3 scripts/image_to_ascii.py --width 100

    # Plain text output
    python3 scripts/image_to_ascii.py --format txt --output image/ascii_art.txt
"""

import argparse
import sys
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


# Character sets ordered from darkest (most dense) to lightest (least dense)
CHARSETS = {
    # Dense — more characters = better gradient mapping for portraits
    "dense": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    # Standard — classic ASCII art
    "standard": "@#S%?*+;:,. ",
    # Minimal — bold, high contrast
    "minimal": "@#=- ",
    # Block — unicode blocks
    "block": "█▓▒░ ",
}


def load_image(path: str) -> Image.Image:
    """Load and return an image from the given path."""
    img_path = Path(path)
    if not img_path.exists():
        print(f"Error: Image not found at '{path}'")
        sys.exit(1)
    return Image.open(img_path)


def resize_image(image: Image.Image, new_width: int) -> Image.Image:
    """
    Resize image to the target width while maintaining aspect ratio.
    Accounts for monospace character aspect ratio (~0.55 height:width).
    """
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)
    return image.resize((new_width, new_height), Image.LANCZOS)


def image_to_colored_svg(
    input_path: str,
    width: int = 80,
    charset: str = "dense",
    font_size: int = 10,
    bg_color: str = "#0D1117",
) -> str:
    """
    Convert an image to a colored ASCII art SVG.

    Each character is rendered in the color of the corresponding pixel
    from the original image, producing a faithful color representation.
    """
    chars = CHARSETS.get(charset, CHARSETS["dense"])
    num_chars = len(chars)

    # Load image
    image = load_image(input_path)
    image = resize_image(image, width)

    # Get dimensions after resize
    img_width, img_height = image.size

    # Convert to RGB for color extraction
    color_image = image.convert("RGB")
    # Convert to grayscale for character mapping
    gray_image = image.convert("L")

    color_pixels = list(color_image.getdata())
    gray_pixels = list(gray_image.getdata())

    # Character dimensions in the SVG
    char_width = font_size * 0.6  # monospace char width approximation
    char_height = font_size * 1.2  # line height

    svg_width = int(img_width * char_width) + 20  # padding
    svg_height = int(img_height * char_height) + 20  # padding

    # Build SVG
    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                     f'viewBox="0 0 {svg_width} {svg_height}" '
                     f'width="{svg_width}" height="{svg_height}">')
    svg_lines.append(f'  <rect width="100%" height="100%" fill="{bg_color}"/>')
    svg_lines.append(f'  <style>')
    svg_lines.append(f'    text {{')
    svg_lines.append(f'      font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace;')
    svg_lines.append(f'      font-size: {font_size}px;')
    svg_lines.append(f'      white-space: pre;')
    svg_lines.append(f'    }}')
    svg_lines.append(f'  </style>')

    # Generate each row as a <text> element with colored <tspan>s
    for row in range(img_height):
        y_pos = 10 + (row + 1) * char_height
        row_spans = []
        prev_color = None
        current_run = ""

        for col in range(img_width):
            idx = row * img_width + col
            # Get brightness for character selection
            brightness = gray_pixels[idx]
            char_idx = brightness * (num_chars - 1) // 255
            char = chars[char_idx]

            # Get pixel color
            r, g, b = color_pixels[idx]
            hex_color = f"#{r:02x}{g:02x}{b:02x}"

            if hex_color == prev_color:
                current_run += escape(char)
            else:
                if current_run:
                    row_spans.append(f'<tspan fill="{prev_color}">{current_run}</tspan>')
                current_run = escape(char)
                prev_color = hex_color

        # Flush last run
        if current_run:
            row_spans.append(f'<tspan fill="{prev_color}">{current_run}</tspan>')

        svg_lines.append(f'  <text x="10" y="{y_pos:.1f}">{"".join(row_spans)}</text>')

    svg_lines.append('</svg>')
    return "\n".join(svg_lines)


def image_to_plain_ascii(
    input_path: str,
    width: int = 50,
    charset: str = "dense",
) -> str:
    """Convert an image to plain text ASCII art (no color)."""
    chars = CHARSETS.get(charset, CHARSETS["dense"])
    num_chars = len(chars)

    image = load_image(input_path)
    image = resize_image(image, width)
    gray_image = image.convert("L")

    # Apply contrast enhancement
    gray_image = gray_image.point(lambda x: min(255, max(0, int((x - 128) * 1.3 + 128))))

    pixels = list(gray_image.getdata())
    img_width, img_height = gray_image.size

    lines = []
    for row in range(img_height):
        line = ""
        for col in range(img_width):
            idx = row * img_width + col
            brightness = pixels[idx]
            char_idx = brightness * (num_chars - 1) // 255
            line += chars[char_idx]
        lines.append(line)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Convert an image to colored ASCII art (SVG) for GitHub README"
    )
    parser.add_argument(
        "--input", "-i",
        default="image/eml.jpg",
        help="Path to input image (default: image/eml.jpg)",
    )
    parser.add_argument(
        "--output", "-o",
        default="image/ascii_portrait.svg",
        help="Path to output file (default: image/ascii_portrait.svg)",
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=80,
        help="Width in characters (default: 80)",
    )
    parser.add_argument(
        "--chars", "-c",
        choices=list(CHARSETS.keys()),
        default="dense",
        help="Character set to use (default: dense)",
    )
    parser.add_argument(
        "--font-size", "-fs",
        type=int,
        default=10,
        help="Font size in pixels for SVG output (default: 10)",
    )
    parser.add_argument(
        "--bg",
        default="#0D1117",
        help="Background color for SVG (default: #0D1117, GitHub dark)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["svg", "txt"],
        default="svg",
        help="Output format: svg (colored) or txt (plain) (default: svg)",
    )

    args = parser.parse_args()

    print(f"Converting: {args.input}")
    print(f"Width: {args.width} chars | Charset: {args.chars} | Format: {args.format}")

    if args.format == "svg":
        result = image_to_colored_svg(
            args.input, args.width, args.chars, args.font_size, args.bg
        )
    else:
        result = image_to_plain_ascii(args.input, args.width, args.chars)

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")

    print(f"Saved to: {args.output}")
    print(f"\nDone. Embed in README with:")
    if args.format == "svg":
        print(f'  <img src="./{args.output}" alt="ASCII Portrait"/>')
    else:
        print(f"  Paste contents inside a ``` code block")


if __name__ == "__main__":
    main()
