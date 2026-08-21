#!/usr/bin/env python3
"""
Convert an image to ASCII art for GitHub profile README.
Produces output similar to neofetch-style ASCII portraits.

Usage:
    python3 scripts/image_to_ascii.py [--input IMAGE_PATH] [--output OUTPUT_PATH]
                                       [--width COLS] [--chars CHARSET]

Defaults:
    --input   image/eml.jpg
    --output  image/ascii_art.txt
    --width   50
    --chars   dense  (options: dense, standard, minimal)
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


# Character sets ordered from darkest (most dense) to lightest (least dense)
CHARSETS = {
    # Dense set — more characters gives better gradients, great for portraits
    "dense": "@%#*+=-:. ",
    # Standard — classic ASCII art feel
    "standard": "@#S%?*+;:,. ",
    # Minimal — fewer chars, bolder look
    "minimal": "@#=- ",
    # Block — uses unicode block characters for a pixel-ish feel
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
    Accounts for terminal character aspect ratio (~2:1 height:width).
    """
    width, height = image.size
    aspect_ratio = height / width
    # Characters are roughly twice as tall as they are wide
    new_height = int(aspect_ratio * new_width * 0.55)
    return image.resize((new_width, new_height))


def pixels_to_ascii(image: Image.Image, chars: str) -> str:
    """Convert grayscale pixel values to ASCII characters."""
    pixels = list(image.getdata())
    num_chars = len(chars)
    ascii_pixels = []
    for pixel in pixels:
        # Map pixel brightness (0-255) to character index
        index = pixel * (num_chars - 1) // 255
        ascii_pixels.append(chars[index])
    return "".join(ascii_pixels)


def image_to_ascii(
    input_path: str,
    width: int = 50,
    charset: str = "dense",
) -> str:
    """
    Convert an image file to ASCII art string.

    Args:
        input_path: Path to the source image
        width: Number of characters per line
        charset: Which character set to use

    Returns:
        The ASCII art as a multiline string
    """
    chars = CHARSETS.get(charset, CHARSETS["dense"])

    # Load and process
    image = load_image(input_path)
    image = resize_image(image, width)
    image = image.convert("L")  # Convert to grayscale

    # Apply slight contrast enhancement for better ASCII output
    # Darken shadows and brighten highlights
    image = image.point(lambda x: min(255, max(0, int((x - 128) * 1.3 + 128))))

    # Convert to ASCII
    ascii_str = pixels_to_ascii(image, chars)

    # Split into lines
    lines = [ascii_str[i : i + width] for i in range(0, len(ascii_str), width)]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Convert an image to ASCII art for GitHub README"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="image/eml.jpg",
        help="Path to input image (default: image/eml.jpg)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="image/ascii_art.txt",
        help="Path to output text file (default: image/ascii_art.txt)",
    )
    parser.add_argument(
        "--width",
        "-w",
        type=int,
        default=50,
        help="Width in characters (default: 50)",
    )
    parser.add_argument(
        "--chars",
        "-c",
        choices=list(CHARSETS.keys()),
        default="dense",
        help="Character set to use (default: dense)",
    )
    parser.add_argument(
        "--preview",
        "-p",
        action="store_true",
        help="Print preview to terminal",
    )

    args = parser.parse_args()

    print(f"Converting: {args.input}")
    print(f"Width: {args.width} chars | Charset: {args.chars}")

    ascii_art = image_to_ascii(args.input, args.width, args.chars)

    # Save to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(ascii_art, encoding="utf-8")
    print(f"Saved to: {args.output}")

    if args.preview:
        print("\n--- Preview ---\n")
        print(ascii_art)

    print("\nDone. You can now update your README.md with the generated ASCII art.")


if __name__ == "__main__":
    main()
