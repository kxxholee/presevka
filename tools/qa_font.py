from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.ttLib import TTFont

from fontTools.pens.recordingPen import DecomposingRecordingPen

from font_utils import (
    PRESEVKA_HANGUL_CELL,
    PRESEVKA_LATIN_CELL,
    PRESEVKA_POST_ITALIC_ANGLE,
    PRESEVKA_SLOPES,
    PRESEVKA_WEIGHTS,
    STRICT_HANGUL_RANGES,
    best_cmap,
    glyph_bounds,
    in_ranges,
    presevka_legacy_names,
    presevka_style_name,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Verify the final 480/960 font geometry and mappings."
    )
    p.add_argument("font", type=Path)
    p.add_argument("--family", default="Presevka")
    p.add_argument("--weight", choices=PRESEVKA_WEIGHTS, default="Regular")
    p.add_argument("--slope", choices=PRESEVKA_SLOPES, default="Upright")
    p.add_argument("--weight-class", type=int, default=400)
    p.add_argument("--version", default="0.4.0")
    p.add_argument("--font-revision", type=float, default=0.4)
    p.add_argument("--hangul-source", type=Path)
    return p.parse_args()


def decomposed_outline(font: TTFont, glyph_name: str):
    pen = DecomposingRecordingPen(font.getGlyphSet())
    font.getGlyphSet()[glyph_name].draw(pen)
    return pen.value


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
        if latin_widths != {PRESEVKA_LATIN_CELL}:
            raise RuntimeError(
                f"Latin sample is not exactly {PRESEVKA_LATIN_CELL} units: "
                f"{sorted(latin_widths)}"
            )

        modern = [cp for cp in range(0xAC00, 0xD7A4) if cp in cmap]
        if len(modern) != 11172:
            raise RuntimeError(f"modern Hangul coverage: {len(modern)}/11172")

        strict_widths = {
            hmtx.metrics[name][0]
            for cp, name in cmap.items()
            if in_ranges(cp, STRICT_HANGUL_RANGES) and name in hmtx.metrics
        }
        if strict_widths != {PRESEVKA_HANGUL_CELL}:
            raise RuntimeError(
                f"Hangul strict widths are not {PRESEVKA_HANGUL_CELL}: "
                f"{sorted(strict_widths)}"
            )

        min_left = float("inf")
        min_right = float("inf")
        for cp in modern:
            name = cmap[cp]
            bounds = glyph_bounds(font, name)
            if bounds is None:
                continue
            x_min, _, x_max, _ = bounds
            min_left = min(min_left, x_min)
            min_right = min(min_right, PRESEVKA_HANGUL_CELL - x_max)
        if min_left < -2 or min_right < -2:
            raise RuntimeError(
                f"Hangul ink crosses its {PRESEVKA_HANGUL_CELL}-unit cell: "
                f"left={min_left}, right={min_right}"
            )

        strict_ink_radius = 0.0
        strict_center = PRESEVKA_HANGUL_CELL / 2.0
        for cp, name in cmap.items():
            if not in_ranges(cp, STRICT_HANGUL_RANGES):
                continue
            bounds = glyph_bounds(font, name)
            if bounds is None:
                continue
            x_min, _, x_max, _ = bounds
            strict_ink_radius = max(
                strict_ink_radius,
                strict_center - x_min,
                x_max - strict_center,
            )
        actual_ink_width = strict_ink_radius * 2
        if actual_ink_width >= PRESEVKA_HANGUL_CELL:
            raise RuntimeError(
                f"Hangul ink envelope must remain inside its cell: "
                f"{actual_ink_width} >= {PRESEVKA_HANGUL_CELL}"
            )

        style = presevka_style_name(args.weight, args.slope)
        full_name = args.family if style == "Regular" else f"{args.family} {style}"
        legacy_family, legacy_subfamily = presevka_legacy_names(
            args.family, args.weight, args.slope
        )
        expected_names = {
            1: legacy_family,
            2: legacy_subfamily,
            3: f"{args.family}:{style}:{args.version}",
            4: full_name,
            5: f"Version {args.version}",
            6: f"{args.family}-" + "".join(ch for ch in style if ch.isalnum()),
            16: args.family,
            17: style,
            21: args.family,
            22: style,
        }
        for name_id, expected in expected_names.items():
            actual = {
                r.toUnicode() for r in font["name"].names if r.nameID == name_id
            }
            if actual != {expected}:
                raise RuntimeError(
                    f"name ID {name_id} must be exactly {expected!r}; got {sorted(actual)}"
                )

        # OpenType stores this as 16.16 fixed point, so allow one storage unit.
        revision_tolerance = 1 / 65536
        if abs(font["head"].fontRevision - args.font_revision) > revision_tolerance:
            raise RuntimeError(
                f"font revision must be {args.font_revision}, "
                f"got {font['head'].fontRevision}"
            )

        public_name_values = {
            r.toUnicode()
            for r in font["name"].names
            if r.nameID in {1, 3, 4, 6, 16, 17}
        }
        stale = sorted(
            v
            for v in public_name_values
            if "Presevka Base" in v or "PresevkaBase" in v
        )
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
        if "OS/2" not in font or font["OS/2"].usWeightClass != args.weight_class:
            actual = font["OS/2"].usWeightClass if "OS/2" in font else None
            raise RuntimeError(
                f"weight class must be {args.weight_class}, got {actual}"
            )

        is_italic = args.slope == "Italic"
        fs_selection = font["OS/2"].fsSelection
        if bool(fs_selection & (1 << 0)) != is_italic:
            raise RuntimeError(
                f"OS/2 italic flag mismatch for {args.slope}: {fs_selection}"
            )
        if fs_selection & (1 << 9):
            raise RuntimeError(f"face must not be marked oblique: {fs_selection}")
        if bool(font["head"].macStyle & (1 << 1)) != is_italic:
            raise RuntimeError(
                f"head.macStyle italic mismatch for {args.slope}: "
                f"{font['head'].macStyle}"
            )
        expected_angle = PRESEVKA_POST_ITALIC_ANGLE if is_italic else 0.0
        if abs(font["post"].italicAngle - expected_angle) > 0.01:
            raise RuntimeError(
                f"italic angle must be {expected_angle}, "
                f"got {font['post'].italicAngle}"
            )

        if args.hangul_source:
            source = TTFont(args.hangul_source)
            try:
                source_cmap = best_cmap(source)
                # These samples cover compatibility Jamo and widely different
                # modern-syllable constructions. Exact equality ensures that
                # Italic faces keep the upright Pretendard outlines.
                upright_samples = (0x3131, 0x314F, 0xAC00, 0xAC01, 0xB098, 0xD7A3)
                for cp in upright_samples:
                    if cp not in cmap or cp not in source_cmap:
                        raise RuntimeError(f"upright Hangul sample U+{cp:04X} is missing")
                    actual_outline = decomposed_outline(font, cmap[cp])
                    source_outline = decomposed_outline(source, source_cmap[cp])
                    if actual_outline != source_outline:
                        raise RuntimeError(
                            f"Hangul outline U+{cp:04X} differs from upright donor"
                        )
                    if hmtx.metrics[cmap[cp]] != source["hmtx"].metrics[source_cmap[cp]]:
                        raise RuntimeError(
                            f"Hangul metrics U+{cp:04X} differ from upright donor"
                        )
            finally:
                source.close()

        print(f"PASS: {args.font}")
        print("UPM: 1000")
        print(f"Latin advance: {PRESEVKA_LATIN_CELL}")
        print(f"Hangul advance: {PRESEVKA_HANGUL_CELL}")
        print(f"Hangul ink envelope: {actual_ink_width:.1f}")
        print(f"Style: {style} ({args.weight_class})")
        print(f"Modern Hangul mappings: {len(modern)}")
        print(f"Minimum modern-Hangul ink margins: left={min_left:.1f}, right={min_right:.1f}")
    finally:
        font.close()


if __name__ == "__main__":
    main()
