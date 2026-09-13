from __future__ import annotations

import argparse
from pathlib import Path
from fontTools.ttLib import TTFont
from font_utils import best_cmap, latin_cell

p = argparse.ArgumentParser()
p.add_argument("font", type=Path)
p.add_argument("--weight-class", type=int, default=400)
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
    if cell != 432 or widths != {432}:
        raise SystemExit(f"Iosevka width mismatch: probe={cell}, sample={sorted(widths)}")
    if "OS/2" not in font or font["OS/2"].usWeightClass != args.weight_class:
        actual = font["OS/2"].usWeightClass if "OS/2" in font else None
        raise SystemExit(
            f"Iosevka weight mismatch: expected {args.weight_class}, got {actual}"
        )
    print(
        f"PASS: Iosevka UPM={upem}, Latin cell={cell}, "
        f"weight={args.weight_class}"
    )
finally:
    font.close()
