#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=11.0",
# ]
# ///

"""Render reproducible light/dark README banners for Presevka.

Default composition:
    프리   -> Presevka SemiBold
    텐다드 -> Presevka Thin
    ×      -> Presevka Thin
    Io     -> Presevka Thin
    sevka  -> Presevka SemiBold

Both light and dark images share the exact same measured layout; only the
palette changes. This keeps the glyph positions pixel-identical.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Segment:
    text: str
    weight: str  # "thin" or "semibold"


SEGMENTS = (
    Segment("프리", "semibold"),
    Segment("텐다드", "thin"),
    Segment(" × ", "thin"),
    Segment("Io", "thin"),
    Segment("sevka", "semibold"),
)


PALETTES = {
    "light": {
        "foreground": "#111111",
    },
    "dark": {
        "foreground": "#f0f6fc",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render Presevka README banners with exact mixed-weight layout."
    )
    parser.add_argument("--width", type=int, default=1800)
    parser.add_argument("--height", type=int, default=460)
    parser.add_argument("--font-size", type=int, default=190)
    parser.add_argument("--padding-x", type=int, default=90)
    parser.add_argument("--padding-y", type=int, default=60)
    parser.add_argument(
        "--font-dir",
        type=Path,
        default=ROOT / "dist",
        help="Directory containing Presevka-Thin.ttf and Presevka-SemiBold.ttf",
    )
    parser.add_argument("--thin-font", type=Path)
    parser.add_argument("--semibold-font", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "assets",
    )
    parser.add_argument(
        "--prefix",
        default="presevka-banner",
        help="Output basename prefix",
    )
    return parser.parse_args()


def resolve_font(explicit: Path | None, font_dir: Path, filename: str) -> Path:
    if explicit is not None:
        path = explicit.expanduser().resolve()
        if not path.is_file():
            raise SystemExit(f"font not found: {path}")
        return path

    font_dir = font_dir.expanduser().resolve()
    direct = font_dir / filename
    if direct.is_file():
        return direct

    matches = sorted(font_dir.rglob(filename)) if font_dir.exists() else []
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(
            f"could not find {filename} under {font_dir}\n"
            "Build Presevka first, or pass --thin-font/--semibold-font explicitly."
        )
    raise SystemExit(
        f"multiple {filename} files found under {font_dir}; pass the file explicitly"
    )


def load_fonts(thin_path: Path, semibold_path: Path, size: int):
    return {
        "thin": ImageFont.truetype(str(thin_path), size=size),
        "semibold": ImageFont.truetype(str(semibold_path), size=size),
    }


def segment_width(draw: ImageDraw.ImageDraw, segment: Segment, fonts) -> float:
    return draw.textlength(segment.text, font=fonts[segment.weight])


def measure(draw: ImageDraw.ImageDraw, fonts) -> tuple[float, float, float]:
    total_width = sum(segment_width(draw, segment, fonts) for segment in SEGMENTS)

    # Use a shared baseline and the union of all segment bbox values. This is
    # important for mixed Hangul/Latin rendering with different weights.
    top = float("inf")
    bottom = float("-inf")
    for segment in SEGMENTS:
        bbox = draw.textbbox(
            (0, 0),
            segment.text,
            font=fonts[segment.weight],
            anchor="ls",  # left + baseline
        )
        top = min(top, bbox[1])
        bottom = max(bottom, bbox[3])
    return total_width, top, bottom


def fit_font_size(
    width: int,
    height: int,
    padding_x: int,
    padding_y: int,
    requested_size: int,
    thin_path: Path,
    semibold_path: Path,
) -> tuple[int, dict[str, ImageFont.FreeTypeFont], tuple[float, float, float]]:
    scratch = Image.new("RGB", (8, 8))
    draw = ImageDraw.Draw(scratch)

    size = requested_size
    while size >= 20:
        fonts = load_fonts(thin_path, semibold_path, size)
        metrics = measure(draw, fonts)
        text_width, top, bottom = metrics
        text_height = bottom - top
        if (
            text_width <= width - 2 * padding_x
            and text_height <= height - 2 * padding_y
        ):
            return size, fonts, metrics
        size -= 2

    raise SystemExit("banner dimensions are too small for the requested composition")


def render(
    output: Path,
    palette: dict[str, str],
    width: int,
    height: int,
    fonts,
    metrics: tuple[float, float, float],
) -> None:
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    text_width, top, bottom = metrics
    x = (width - text_width) / 2

    # Position the union of the mixed-weight glyph ink vertically in the canvas.
    ink_height = bottom - top
    desired_top = (height - ink_height) / 2
    baseline_y = desired_top - top

    for segment in SEGMENTS:
        font = fonts[segment.weight]
        draw.text(
            (round(x), round(baseline_y)),
            segment.text,
            font=font,
            fill=palette["foreground"],
            anchor="ls",
        )
        x += draw.textlength(segment.text, font=font)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def main() -> None:
    args = parse_args()
    if args.width <= 0 or args.height <= 0 or args.font_size <= 0:
        raise SystemExit("width, height, and font-size must be positive")

    thin_path = resolve_font(args.thin_font, args.font_dir, "Presevka-Thin.ttf")
    semibold_path = resolve_font(
        args.semibold_font, args.font_dir, "Presevka-SemiBold.ttf"
    )

    size, fonts, metrics = fit_font_size(
        args.width,
        args.height,
        args.padding_x,
        args.padding_y,
        args.font_size,
        thin_path,
        semibold_path,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for mode, palette in PALETTES.items():
        output = args.output_dir / f"{args.prefix}-{mode}.png"
        render(output, palette, args.width, args.height, fonts, metrics)
        outputs.append(output)

    print(f"Thin:      {thin_path}")
    print(f"SemiBold:  {semibold_path}")
    print(f"Font size: {size}px")
    print("Composition: 프리[SemiBold] + 텐다드 × Io[Thin] + sevka[SemiBold]")
    for output in outputs:
        print(f"Wrote: {output}")


if __name__ == "__main__":
    main()
