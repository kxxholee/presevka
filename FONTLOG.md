# FONTLOG for Presevka

This file records changes made in Presevka and acknowledges the upstream font
projects whose glyph designs it uses. Presevka is a Modified Version under the
SIL Open Font License, Version 1.1.

## Basic font information

Presevka combines a narrow Iosevka programming-font base with Hangul glyphs
prepared from Pretendard. Its Latin advance width is 432 units and its strict
Hangul advance width is 864 units in a 1000-unit em, so one Hangul cell occupies
exactly two Latin cells.

The public family name and all user-visible naming records use `Presevka`.
`Presevka` is a Reserved Font Name declared by Kwanho Lee (이관호).

## Upstream sources

- Iosevka v34.8.0, copyright Renzhi Li / The Iosevka Project Authors.
- Pretendard v1.3.9 Regular, copyright Kil Hyung-jin and the respective authors
  of its upstream glyph designs.

Exact notices and license terms are recorded in `OFL.txt` and
`THIRD_PARTY.md`.

## ChangeLog

### 2026 - Presevka 0.1.0 - Kwanho Lee (이관호)

- Built the Regular Upright Latin base from Iosevka with a custom 432/1000-em
  advance width, normal spacing, sans-serif construction, and upstream-default
  character variants.
- Used Iosevka's unhinted build because the outlines are subsequently modified
  and merged.
- Converted the static Pretendard Regular CFF outlines to TrueType `glyf`
  outlines when required.
- Normalized the Pretendard donor to a 1000-unit em.
- Horizontally scaled and centered imported Hangul outlines to fit an exact
  864-unit, two-Latin-cell advance.
- Imported modern Hangul syllables and supported Hangul/Jamo ranges from the
  prepared Pretendard donor into the Iosevka base.
- Removed invalidated source hinting and digital-signature data after outline
  modification.
- Recalculated Unicode/code-page coverage and expanded vertical metrics where
  required by imported Hangul outlines.
- Replaced source naming records with the public family name `Presevka` and
  recorded SIL OFL 1.1 licensing metadata.
- Added reproducible build, verification, QA, installation, and CI artifact
  packaging scripts.
