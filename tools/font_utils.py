from __future__ import annotations

from collections.abc import Iterable
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

# Strict 2-cell characters in the resulting monospace font.
STRICT_HANGUL_RANGES = (
    (0x3130, 0x318F),  # Hangul Compatibility Jamo
    (0xAC00, 0xD7A3),  # Modern precomposed Hangul syllables
)

# Imported too, but their original shaping/advance behavior is preserved where
# appropriate instead of blindly forcing every conjoining Jamo to 2 cells.
ALL_HANGUL_RANGES = (
    (0x1100, 0x11FF),  # Hangul Jamo
    (0x3130, 0x318F),  # Hangul Compatibility Jamo
    (0xA960, 0xA97F),  # Jamo Extended-A
    (0xAC00, 0xD7A3),  # Modern precomposed Hangul syllables
    (0xD7B0, 0xD7FF),  # Jamo Extended-B
)


def in_ranges(cp: int, ranges: Iterable[tuple[int, int]]) -> bool:
    return any(start <= cp <= end for start, end in ranges)


def best_cmap(font: TTFont) -> dict[int, str]:
    cmap = font.getBestCmap()
    if cmap is None:
        raise RuntimeError("font has no usable Unicode cmap")
    return cmap


def glyph_bounds(font: TTFont, glyph_name: str):
    glyph_set = font.getGlyphSet()
    pen = BoundsPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    return pen.bounds


def latin_cell(font: TTFont) -> int:
    cmap = best_cmap(font)
    widths: list[int] = []
    for ch in "Mi0 ":
        name = cmap.get(ord(ch))
        if name is None:
            continue
        widths.append(font["hmtx"].metrics[name][0])
    if not widths or len(set(widths)) != 1:
        raise RuntimeError(f"base font is not monospaced for probe glyphs: {widths}")
    return widths[0]
