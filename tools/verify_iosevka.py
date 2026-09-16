from __future__ import annotations

import argparse
from pathlib import Path
from fontTools.ttLib import TTFont
from font_utils import (
    PRESEVKA_LATIN_CELL,
    PRESEVKA_POST_ITALIC_ANGLE,
    PRESEVKA_SLOPES,
    best_cmap,
    latin_cell,
)

p = argparse.ArgumentParser()
p.add_argument("font", type=Path)
p.add_argument("--weight-class", type=int, default=400)
p.add_argument("--slope", choices=PRESEVKA_SLOPES, default="Upright")
args = p.parse_args()
font = TTFont(args.font)
try:
    upem = font["head"].unitsPerEm
    cell = latin_cell(font)
    cmap = best_cmap(font)
    sample = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    widths = {font["hmtx"].metrics[cmap[ord(ch)]][0] for ch in sample if ord(ch) in cmap}
    if upem != 1000:
        raise SystemExit(f"Iosevka UPM mismatch: expected 1000, got {upem}")
    if cell != PRESEVKA_LATIN_CELL or widths != {PRESEVKA_LATIN_CELL}:
        raise SystemExit(f"Iosevka width mismatch: probe={cell}, sample={sorted(widths)}")
    if "OS/2" not in font or font["OS/2"].usWeightClass != args.weight_class:
        actual = font["OS/2"].usWeightClass if "OS/2" in font else None
        raise SystemExit(
            f"Iosevka weight mismatch: expected {args.weight_class}, got {actual}"
        )
    is_italic = args.slope == "Italic"
    fs_selection = font["OS/2"].fsSelection
    if bool(fs_selection & (1 << 0)) != is_italic:
        raise SystemExit(
            f"Iosevka italic flag mismatch for {args.slope}: fsSelection={fs_selection}"
        )
    if fs_selection & (1 << 9):
        raise SystemExit(f"Iosevka face is unexpectedly marked oblique: {fs_selection}")
    if bool(font["head"].macStyle & (1 << 1)) != is_italic:
        raise SystemExit(
            f"Iosevka macStyle italic mismatch for {args.slope}: {font['head'].macStyle}"
        )
    expected_angle = PRESEVKA_POST_ITALIC_ANGLE if is_italic else 0.0
    if abs(font["post"].italicAngle - expected_angle) > 0.01:
        raise SystemExit(
            f"Iosevka italic angle mismatch: expected {expected_angle}, "
            f"got {font['post'].italicAngle}"
        )
    print(
        f"PASS: Iosevka UPM={upem}, Latin cell={cell}, "
        f"weight={args.weight_class}, slope={args.slope}"
    )
finally:
    font.close()
