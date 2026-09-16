from __future__ import annotations

import argparse
import json
from pathlib import Path

from font_utils import (
    ALL_HANGUL_RANGES,
    PRESEVKA_HANGUL_CELL,
    PRESEVKA_HANGUL_OUTLINE_X_SCALE,
    PRESEVKA_LATIN_CELL,
    STRICT_HANGUL_RANGES,
    best_cmap,
    in_ranges,
    latin_cell,
)
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.transform import Transform
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Normalize a static Pretendard weight to the Iosevka UPM and fit Hangul "
            "to exactly two 480-unit Latin cells."
        )
    )
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--base-font", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--report", type=Path)
    return p.parse_args()


def convert_cff_to_truetype(font: TTFont) -> str:
    """Return the source flavor and ensure the working font uses glyf outlines."""
    if "glyf" in font:
        return "truetype"
    if "CFF2" in font:
        raise RuntimeError(
            "Pretendard source is variable/CFF2. Use a static Pretendard OTF file."
        )
    if "CFF " not in font:
        raise RuntimeError("Pretendard source has neither glyf nor CFF outlines")

    glyph_set = font.getGlyphSet()
    max_err = font["head"].unitsPerEm / 1000.0
    glyphs: dict[str, object] = {}

    for glyph_name in font.getGlyphOrder():
        recording = DecomposingRecordingPen(glyph_set)
        glyph_set[glyph_name].draw(recording)
        pen = TTGlyphPen(None)
        recording.replay(Cu2QuPen(pen, max_err=max_err, reverse_direction=True))
        glyphs[glyph_name] = pen.glyph()

    for tag in ("CFF ", "CFF2", "VORG"):
        if tag in font:
            del font[tag]

    builder = FontBuilder(font=font)
    builder.isTTF = True
    font.sfntVersion = "\x00\x01\x00\x00"
    font["head"].glyphDataFormat = 0
    builder.setupGlyf(glyphs)
    builder.setupMaxp()
    return "cff"


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    base = TTFont(args.base_font)
    source = TTFont(args.input)
    try:
        if "OS/2" not in base or "OS/2" not in source:
            raise RuntimeError("both base and donor must contain an OS/2 table")
        base_weight = int(base["OS/2"].usWeightClass)
        source_weight = int(source["OS/2"].usWeightClass)
        if base_weight != source_weight:
            raise RuntimeError(
                f"weight mismatch: Iosevka base is {base_weight}, "
                f"Pretendard donor is {source_weight}"
            )

        source_flavor = convert_cff_to_truetype(source)

        target_upem = int(base["head"].unitsPerEm)
        cell = latin_cell(base)
        target_advance = cell * 2

        if cell != PRESEVKA_LATIN_CELL:
            raise RuntimeError(
                f"expected Iosevka Latin cell {PRESEVKA_LATIN_CELL}, got {cell}; "
                "refusing mismatched build"
            )
        if target_upem != 1000:
            raise RuntimeError(
                f"expected Iosevka UPM 1000, got {target_upem}; update math deliberately"
            )
        if target_advance != PRESEVKA_HANGUL_CELL:
            raise RuntimeError(
                f"expected target Hangul advance {PRESEVKA_HANGUL_CELL}, "
                f"got {target_advance}"
            )
        source_upem = int(source["head"].unitsPerEm)
        cmap = best_cmap(source)
        hmtx = source["hmtx"]

        modern_names = {
            name
            for cp, name in cmap.items()
            if 0xAC00 <= cp <= 0xD7A3 and name in hmtx.metrics
        }
        if len(modern_names) != 11172:
            raise RuntimeError(
                f"Pretendard source has {len(modern_names)} modern Hangul glyphs; expected 11172"
            )

        modern_advances = {hmtx.metrics[name][0] for name in modern_names}
        if len(modern_advances) != 1:
            sample = sorted(modern_advances)[:20]
            raise RuntimeError(
                "Pretendard modern Hangul is not fixed-width; advances=" + repr(sample)
            )
        source_hangul_advance = modern_advances.pop()

        hangul_names = {
            name
            for cp, name in cmap.items()
            if in_ranges(cp, ALL_HANGUL_RANGES) and name in hmtx.metrics
        }

        # The source outlines changed, so source hints/signatures are no longer valid.
        for tag in ("fpgm", "prep", "cvt ", "DSIG"):
            if tag in source:
                del source[tag]
        source["glyf"].removeHinting()

        if source_upem != target_upem:
            scale_upem(source, target_upem)

        # Modern syllables + compatibility jamo are strict 2-cell characters.
        cmap = best_cmap(source)
        hmtx = source["hmtx"]
        glyf = source["glyf"]
        strict_names = {
            name
            for cp, name in cmap.items()
            if in_ranges(cp, STRICT_HANGUL_RANGES) and name in hmtx.metrics
        }

        for name in strict_names:
            glyph = glyf[name]
            glyph.recalcBounds(glyf)
            old_advance, old_lsb = hmtx.metrics[name]
            dx = (target_advance - old_advance) / 2.0
            if dx:
                recording = DecomposingRecordingPen(source.getGlyphSet())
                source.getGlyphSet()[name].draw(recording)
                pen = TTGlyphPen(None)
                recording.replay(
                    TransformPen(pen, Transform(1, 0, 0, 1, dx, 0))
                )
                glyph = pen.glyph()
                glyph.recalcBounds(glyf)
                glyf[name] = glyph
            hmtx.metrics[name] = (
                target_advance,
                int(getattr(glyph, "xMin", old_lsb + round(dx))),
            )

        # Preserve Pretendard's original weight-dependent proportions. Every
        # Hangul/Jamo outline receives the same minimal 2% enlargement, while
        # the wider 960-unit advance is primarily expressed as side bearings.
        fit_center = target_advance / 2.0
        strict_bounds = []
        for name in strict_names:
            glyph = glyf[name]
            glyph.recalcBounds(glyf)
            if getattr(glyph, "numberOfContours", 0) != 0:
                strict_bounds.append((glyph.xMin, glyph.xMax))

        if not strict_bounds:
            raise RuntimeError("no strict Hangul outlines available for ink fitting")
        max_radius_before = max(
            fit_center - min(x_min for x_min, _ in strict_bounds),
            max(x_max for _, x_max in strict_bounds) - fit_center,
        )
        outline_x_scale = PRESEVKA_HANGUL_OUTLINE_X_SCALE
        expected_ink_radius = max_radius_before * outline_x_scale
        fit_glyph_set = source.getGlyphSet()
        for name in hangul_names:
            advance, _ = hmtx.metrics[name]
            center = advance / 2.0
            x_shift = center * (1.0 - outline_x_scale)
            recording = DecomposingRecordingPen(fit_glyph_set)
            fit_glyph_set[name].draw(recording)
            pen = TTGlyphPen(None)
            recording.replay(
                TransformPen(
                    pen,
                    Transform(outline_x_scale, 0, 0, 1.0, x_shift, 0),
                )
            )
            glyph = pen.glyph()
            glyph.recalcBounds(glyf)
            glyf[name] = glyph
            hmtx.metrics[name] = (advance, glyph.xMin)

        source.save(args.output)

        check = TTFont(args.output)
        try:
            if check["head"].unitsPerEm != target_upem:
                raise RuntimeError("prepared donor UPM verification failed")
            check_cmap = best_cmap(check)
            check_hmtx = check["hmtx"]
            check_glyf = check["glyf"]
            widths = {
                check_hmtx.metrics[name][0]
                for cp, name in check_cmap.items()
                if in_ranges(cp, STRICT_HANGUL_RANGES)
                and name in check_hmtx.metrics
            }
            if widths != {target_advance}:
                raise RuntimeError(
                    f"prepared donor width verification failed: {sorted(widths)}"
                )
            check_bounds = []
            for cp, name in check_cmap.items():
                if not in_ranges(cp, STRICT_HANGUL_RANGES):
                    continue
                glyph = check_glyf[name]
                glyph.recalcBounds(check_glyf)
                if getattr(glyph, "numberOfContours", 0) != 0:
                    check_bounds.append((glyph.xMin, glyph.xMax))
            actual_ink_radius = max(
                fit_center - min(x_min for x_min, _ in check_bounds),
                max(x_max for _, x_max in check_bounds) - fit_center,
            )
            if abs(actual_ink_radius - expected_ink_radius) > 1:
                raise RuntimeError(
                    "prepared donor ink envelope verification failed: "
                    f"expected radius {expected_ink_radius}, got {actual_ink_radius}"
                )
        finally:
            check.close()

        report = {
            "source_outline_flavor": source_flavor,
            "weight_class": source_weight,
            "source_upem": source_upem,
            "source_modern_hangul_advance": source_hangul_advance,
            "source_modern_hangul_em": source_hangul_advance / source_upem,
            "target_upem": target_upem,
            "latin_cell": cell,
            "target_hangul_advance": target_advance,
            "target_hangul_em": target_advance / target_upem,
            "natural_max_ink_radius": max_radius_before,
            "outline_x_scale": outline_x_scale,
            "outline_x_change_percent": (outline_x_scale - 1.0) * 100.0,
            "actual_hangul_ink_width": actual_ink_radius * 2,
            "strict_hangul_glyphs": len(strict_names),
            "all_importable_hangul_glyphs": len(hangul_names),
        }
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

        print(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"prepared: {args.output}")
    finally:
        base.close()
        source.close()


if __name__ == "__main__":
    main()
