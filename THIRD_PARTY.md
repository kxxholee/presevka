# Third-party fonts

Presevka uses glyph designs from the following upstream font projects. The
generated font is a Modified Version and remains licensed under the SIL Open
Font License, Version 1.1. The original Presevka build tools are separately
licensed under the MIT License in `LICENSE-CODE`.

## Iosevka

- Repository: https://github.com/be5invis/Iosevka
- Pinned version: v34.8.0
- Copyright: Copyright (c) 2015-2026, Renzhi Li (aka. Belleve Invis)
- License: SIL Open Font License 1.1
- Reserved Font Names: none declared in the pinned version's `LICENSE.md`

Presevka builds Iosevka with a custom 432/1000-em unit width. Character variant
settings are not overridden, so the initial build uses Iosevka's upstream
default glyph design.

## Pretendard

- Repository: https://github.com/orioncactus/pretendard
- Pinned version: v1.3.9
- Copyright: Copyright (c) 2021, Kil Hyung-jin, together with the respective
  authors of the upstream Source, Inter, and M PLUS 1 glyph designs
- License: SIL Open Font License 1.1
- Reserved Font Name declared by the pinned Pretendard license: `Pretendard`

Presevka also conservatively preserves the copyright, trademark, and Reserved
Font Name notices associated with Pretendard's acknowledged upstream designs:
`Source`, `Inter`, and `M PLUS 1`. None of these names is used as Presevka's
primary font name.

Pretendard Regular supplies the Hangul outlines. Presevka converts them to
TrueType outlines when needed, normalizes them to a 1000-unit em, adjusts them
to an 864-unit advance, and merges them into the Iosevka base.

## Presevka modifications

Copyright (c) 2026 Kwanho Lee (이관호), with Reserved Font Name
`Presevka`.

Copyright applies to the original modifications, composition, metric
adjustments, naming, and build system of Presevka. Third-party glyph designs
remain copyright of their respective authors.

The generated Presevka font and its font-specific modifications are licensed
under SIL OFL 1.1. See `OFL.txt` for the consolidated notices and complete
license text, and `FONTLOG.md` for the modification history.
