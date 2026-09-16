from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from font_utils import (
    ALL_HANGUL_RANGES,
    PRESEVKA_LATIN_CELL,
    PRESEVKA_SLOPES,
    PRESEVKA_WEIGHTS,
    best_cmap,
    in_ranges,
    latin_cell,
    presevka_legacy_names,
    presevka_style_name,
)


FONT_VERSION = "0.4.0"
FONT_REVISION = 0.4


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Merge prepared Pretendard Hangul into the custom Iosevka base.")
    p.add_argument("--base", required=True, type=Path)
    p.add_argument("--hangul", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--family", default="Presevka")
    p.add_argument("--weight", choices=PRESEVKA_WEIGHTS, default="Regular")
    p.add_argument("--slope", choices=PRESEVKA_SLOPES, default="Upright")
    return p.parse_args()


def set_names(font: TTFont, family: str, weight: str, slope: str) -> None:
    name = font["name"]
    style = presevka_style_name(weight, slope)
    ps_family = "".join(ch for ch in family if ch.isascii() and ch.isalnum()) or "Presevka"
    ps_style = "".join(ch for ch in style if ch.isascii() and ch.isalnum()) or "Regular"
    ps_name = f"{ps_family}-{ps_style}"
    full = family if style == "Regular" else f"{family} {style}"
    legacy_family, legacy_subfamily = presevka_legacy_names(
        family, weight, slope
    )

    # Iosevka's intermediate build intentionally has a temporary family name
    # ("Presevka Base 480"). Remove *all* old naming records that can expose
    # that build-only name before writing the public Presevka family names.
    rewritten_ids = {0, 1, 2, 3, 4, 5, 6, 13, 14, 16, 17, 18, 21, 22, 25}
    name.names = [record for record in name.names if record.nameID not in rewritten_ids]

    version = f"Version {FONT_VERSION}"
    unique_id = f"Presevka:{style}:{FONT_VERSION}"
    copyright_notice = (
        "Iosevka Copyright (c) 2015-2026 Renzhi Li; "
        "Pretendard Copyright (c) 2021 Kil Hyung-jin and its upstream authors; "
        "Presevka modifications Copyright (c) 2026 Kwanho Lee (\uc774\uad00\ud638)."
    )
    values = {
        0: copyright_notice,
        1: legacy_family,
        2: legacy_subfamily,
        3: unique_id,
        4: full,
        5: version,
        6: ps_name,
        13: "SIL Open Font License 1.1; see accompanying OFL.txt.",
        14: "https://openfontlicense.org/open-font-license-official-text/",
        16: family,
        17: style,
        21: family,
        22: style,
    }

    # Windows Unicode English + Macintosh Roman English are enough for broad
    # compatibility once stale source records have been removed. Mac Roman
    # cannot encode the Korean form of the copyright holder's name.
    for nid, value in values.items():
        name.setName(value, nid, 3, 1, 0x409)
        mac_value = value.replace("Kwanho Lee (\uc774\uad00\ud638)", "Kwanho Lee")
        name.setName(mac_value, nid, 1, 0, 0)

    font["head"].fontRevision = FONT_REVISION


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    base = TTFont(args.base)
    donor = TTFont(args.hangul)
    try:
        if "glyf" not in base or "glyf" not in donor:
            raise RuntimeError("both base and donor must be TrueType/glyf fonts")
        if base["head"].unitsPerEm != donor["head"].unitsPerEm:
            raise RuntimeError("base and donor UPM do not match")
        if "OS/2" not in base or "OS/2" not in donor:
            raise RuntimeError("both base and donor must contain an OS/2 table")
        if base["OS/2"].usWeightClass != donor["OS/2"].usWeightClass:
            raise RuntimeError(
                "base and donor weight classes do not match: "
                f"{base['OS/2'].usWeightClass} != {donor['OS/2'].usWeightClass}"
            )
        if latin_cell(base) != PRESEVKA_LATIN_CELL:
            raise RuntimeError(
                f"base Latin cell is not {PRESEVKA_LATIN_CELL}"
            )

        donor_cmap = best_cmap(donor)
        donor_hmtx = donor["hmtx"]
        donor_glyph_set = donor.getGlyphSet()
        base_glyf = base["glyf"]
        base_hmtx = base["hmtx"]

        glyph_order = list(base.getGlyphOrder())
        used_names = set(glyph_order)
        mapping: dict[int, str] = {}

        for cp in sorted(cp for cp in donor_cmap if in_ranges(cp, ALL_HANGUL_RANGES)):
            source_name = donor_cmap[cp]
            if source_name not in donor_hmtx.metrics:
                continue
            new_name = f"presevka.ko.u{cp:04X}"
            suffix = 1
            while new_name in used_names:
                suffix += 1
                new_name = f"presevka.ko.u{cp:04X}.{suffix}"

            recording = DecomposingRecordingPen(donor_glyph_set)
            donor_glyph_set[source_name].draw(recording)
            pen = TTGlyphPen(None)
            recording.replay(pen)
            glyph = pen.glyph()
            glyph.recalcBounds(base_glyf)

            advance, lsb = donor_hmtx.metrics[source_name]
            base_glyf.glyphs[new_name] = glyph
            base_hmtx.metrics[new_name] = (advance, lsb)
            glyph_order.append(new_name)
            used_names.add(new_name)
            mapping[cp] = new_name

        if len(mapping) < 11172:
            raise RuntimeError(f"only {len(mapping)} Hangul mappings prepared; expected at least 11172")

        base.setGlyphOrder(glyph_order)
        base["maxp"].numGlyphs = len(glyph_order)
        if "hhea" in base:
            base["hhea"].numberOfHMetrics = len(glyph_order)

        # Add/replace Hangul mappings in every Unicode cmap subtable that can hold BMP codepoints.
        for table in base["cmap"].tables:
            if not table.isUnicode():
                continue
            table.cmap.update(mapping)

        # Keep OS/2 coverage metadata in sync so font selectors know this font
        # really contains Hangul. This matters especially outside fontconfig.
        if "OS/2" in base:
            base["OS/2"].recalcUnicodeRanges(base)
            if base["OS/2"].version >= 1:
                base["OS/2"].recalcCodePageRanges(base)

        # Expand vertical safety metrics only when the imported Hangul needs it.
        # Iosevka's original metrics otherwise remain unchanged.
        hangul_bounds = []
        for glyph_name in mapping.values():
            glyph = base_glyf[glyph_name]
            glyph.recalcBounds(base_glyf)
            if getattr(glyph, "numberOfContours", 0) != 0:
                hangul_bounds.append((glyph.yMin, glyph.yMax))
        if hangul_bounds:
            guard = 16
            min_y = min(y0 for y0, _ in hangul_bounds)
            max_y = max(y1 for _, y1 in hangul_bounds)
            if "hhea" in base:
                base["hhea"].ascent = max(base["hhea"].ascent, max_y + guard)
                base["hhea"].descent = min(base["hhea"].descent, min_y - guard)
            if "OS/2" in base:
                os2 = base["OS/2"]
                os2.sTypoAscender = max(os2.sTypoAscender, max_y + guard)
                os2.sTypoDescender = min(os2.sTypoDescender, min_y - guard)
                os2.usWinAscent = max(os2.usWinAscent, max_y + guard)
                os2.usWinDescent = max(os2.usWinDescent, -min_y + guard)

        # The Italic base contains Iosevka's native Italic designs. Hangul is
        # deliberately copied from the same upright Pretendard donor without
        # slanting or otherwise synthesizing its outlines.
        set_names(base, args.family, args.weight, args.slope)
        if "DSIG" in base:
            del base["DSIG"]

        base.save(args.output)
        # Round-trip smoke test.
        check = TTFont(args.output)
        check.close()
        print(f"merged {len(mapping)} Hangul codepoints -> {args.output}")
    finally:
        base.close()
        donor.close()


if __name__ == "__main__":
    main()
