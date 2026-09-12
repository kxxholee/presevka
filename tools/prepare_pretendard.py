from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.misc.transform import Transform
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem

from font_utils import (
    ALL_HANGUL_RANGES,
    STRICT_HANGUL_RANGES,
    best_cmap,
    in_ranges,
    latin_cell,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Normalize Pretendard Regular to the Iosevka UPM and fit Hangul "
            "to exactly two 432-unit Latin cells."
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
            "Pretendard source is variable/CFF2. Use the static Pretendard-Regular.otf file."
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
        source_flavor = convert_cff_to_truetype(source)

        target_upem = int(base["head"].unitsPerEm)
        cell = latin_cell(base)
        target_advance = cell * 2

        if cell != 432:
            raise RuntimeError(
                f"expected Iosevka Latin cell 432, got {cell}; refusing mismatched build"
            )
        if target_upem != 1000:
            raise RuntimeError(
                f"expected Iosevka UPM 1000, got {target_upem}; update math deliberately"
            )
        if target_advance != 864:
            raise RuntimeError(f"expected target Hangul advance 864, got {target_advance}")

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

        # Exact em-ratio conversion. If current Pretendard remains 1770/2048,
        # this is about 0.9997016949, only ~0.02983% narrower.
        x_scale = (target_advance / target_upem) / (
            source_hangul_advance / source_upem
        )

        glyph_set = source.getGlyphSet()
        glyf = source["glyf"]
        replacements: dict[str, object] = {}
        hangul_names = {
            name
            for cp, name in cmap.items()
            if in_ranges(cp, ALL_HANGUL_RANGES) and name in hmtx.metrics
        }

        for name in hangul_names:
            advance, lsb = hmtx.metrics[name]
            recording = DecomposingRecordingPen(glyph_set)
            glyph_set[name].draw(recording)
            pen = TTGlyphPen(None)
            x_shift = advance * (1.0 - x_scale) / 2.0
            recording.replay(
                TransformPen(pen, Transform(x_scale, 0, 0, 1.0, x_shift, 0))
            )
            glyph = pen.glyph()
            glyph.recalcBounds(glyf)
            replacements[name] = glyph
            hmtx.metrics[name] = (
                advance,
                int(getattr(glyph, "xMin", round(lsb * x_scale + x_shift))),
            )

        for name, glyph in replacements.items():
            glyf[name] = glyph

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

        source.save(args.output)

        check = TTFont(args.output)
        try:
            if check["head"].unitsPerEm != target_upem:
                raise RuntimeError("prepared donor UPM verification failed")
            check_cmap = best_cmap(check)
            check_hmtx = check["hmtx"]
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
        finally:
            check.close()

        report = {
            "source_outline_flavor": source_flavor,
            "source_upem": source_upem,
            "source_modern_hangul_advance": source_hangul_advance,
            "source_modern_hangul_em": source_hangul_advance / source_upem,
            "target_upem": target_upem,
            "latin_cell": cell,
            "target_hangul_advance": target_advance,
            "target_hangul_em": target_advance / target_upem,
            "x_scale": x_scale,
            "x_change_percent": (x_scale - 1.0) * 100.0,
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
