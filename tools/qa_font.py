from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.ttLib import TTFont

from font_utils import STRICT_HANGUL_RANGES, best_cmap, glyph_bounds, in_ranges


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Verify the final 432/864 font geometry and mappings.")
    p.add_argument("font", type=Path)
    p.add_argument("--family", default="Presevka")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    font = TTFont(args.font)
    try:
        upem = font["head"].unitsPerEm
        if upem != 1000:
            raise RuntimeError(f"UPM must be 1000, got {upem}")

        cmap = best_cmap(font)
        hmtx = font["hmtx"]

        latin_sample = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        latin_widths = {
            hmtx.metrics[cmap[ord(ch)]][0]
            for ch in latin_sample
            if ord(ch) in cmap
        }
        if latin_widths != {432}:
            raise RuntimeError(f"Latin sample is not exactly 432 units: {sorted(latin_widths)}")

        modern = [cp for cp in range(0xAC00, 0xD7A4) if cp in cmap]
        if len(modern) != 11172:
            raise RuntimeError(f"modern Hangul coverage: {len(modern)}/11172")

        strict_widths = {
            hmtx.metrics[name][0]
            for cp, name in cmap.items()
            if in_ranges(cp, STRICT_HANGUL_RANGES) and name in hmtx.metrics
        }
        if strict_widths != {864}:
            raise RuntimeError(f"Hangul strict widths are not 864: {sorted(strict_widths)}")

        min_left = float("inf")
        min_right = float("inf")
        for cp in modern:
            name = cmap[cp]
            bounds = glyph_bounds(font, name)
            if bounds is None:
                continue
            x_min, _, x_max, _ = bounds
            min_left = min(min_left, x_min)
            min_right = min(min_right, 864 - x_max)
        if min_left < -2 or min_right < -2:
            raise RuntimeError(
                f"Hangul ink crosses its 864-unit cell: left={min_left}, right={min_right}"
            )

        families = {r.toUnicode() for r in font["name"].names if r.nameID in {1, 16}}
        if families != {args.family}:
            raise RuntimeError(
                f"family names must be exactly {args.family!r}; got {sorted(families)}"
            )
        public_name_values = {
            r.toUnicode()
            for r in font["name"].names
            if r.nameID in {1, 3, 4, 6, 16, 17}
        }
        stale = sorted(v for v in public_name_values if "Base 432" in v or "PresevkaBase432" in v)
        if stale:
            raise RuntimeError(f"stale build-only font names remain: {stale}")

        copyright_values = {
            r.toUnicode() for r in font["name"].names if r.nameID == 0
        }
        if not copyright_values or not all(
            "Kwanho Lee" in value for value in copyright_values
        ):
            raise RuntimeError("Presevka copyright notice is missing from font metadata")
        if not any("Kwanho Lee (\uc774\uad00\ud638)" in value for value in copyright_values):
            raise RuntimeError("Unicode copyright metadata is missing the Korean holder name")

        license_values = {
            r.toUnicode() for r in font["name"].names if r.nameID == 13
        }
        if not license_values or not all(
            "SIL Open Font License 1.1" in value for value in license_values
        ):
            raise RuntimeError("SIL OFL 1.1 notice is missing from font metadata")

        if "OS/2" in font and font["OS/2"].fsType != 0:
            raise RuntimeError(
                f"OS/2 fsType must permit OFL use and embedding, got {font['OS/2'].fsType}"
            )

        print(f"PASS: {args.font}")
        print("UPM: 1000")
        print("Latin advance: 432")
        print("Hangul advance: 864")
        print(f"Modern Hangul mappings: {len(modern)}")
        print(f"Minimum modern-Hangul ink margins: left={min_left:.1f}, right={min_right:.1f}")
    finally:
        font.close()


if __name__ == "__main__":
    main()
