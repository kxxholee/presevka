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
- Pretendard v1.3.9 static weights, copyright Kil Hyung-jin and the respective authors
  of its upstream glyph designs.

Exact notices and license terms are recorded in `OFL.txt` and
`THIRD_PARTY.md`.

## ChangeLog

### 14 September 2026 - Presevka 0.3.0 - Kwanho Lee (이관호)

- Added native Iosevka Italic faces for all nine weights, producing eighteen
  static Upright and Italic TTF files in total.
- Kept all imported Pretendard Hangul and Jamo outlines upright in Italic faces
  instead of applying synthetic slanting.
- Added slope-aware OpenType naming and metadata verification, including style
  linking, italic flags, and italic angle checks.
- Added QA comparison against the prepared upright Pretendard donor to prevent
  accidental Hangul slanting in future builds.

### 13 September 2026 - Presevka 0.2.0 - Kwanho Lee (이관호)

- Expanded the initial Regular-only build to nine static weights: Thin,
  ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, and Black.
- Matched each Iosevka weight with the corresponding static Pretendard donor.
- Added weight-aware family naming and `OS/2` weight-class verification.
- Applied one uniform horizontal fit per heavy Hangul weight when necessary to
  keep every strict Hangul glyph inside its 864-unit cell.
- Updated installation and CI artifact packaging to include all nine weights.
- Limited the default Iosevka build concurrency to two jobs for predictable CI
  memory use, with `IOSEVKA_JOBS` available as an override.

### 13 September 2026 - Presevka 0.1.0 - Kwanho Lee (이관호)

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
