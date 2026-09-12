# Third-party fonts

This repository contains original orchestration/build code only. It does **not**
redistribute the upstream font binaries in Git. The build clones the fonts from
their official repositories and produces a modified merged font locally.

## Iosevka

- Repository: https://github.com/be5invis/Iosevka
- Copyright: Renzhi Li / The Iosevka Project Authors
- License: SIL Open Font License 1.1

Presevka builds Iosevka with a custom 432/1000-em unit width. Character variant
settings are intentionally not overridden, so the initial build uses Iosevka's
upstream default glyph design.

## Pretendard

- Repository: https://github.com/orioncactus/pretendard
- Copyright: Kil Hyung-jin and upstream authors listed in Pretendard's license
- License: SIL Open Font License 1.1
- Reserved Font Names in Pretendard's license include `Pretendard`, `Source`,
  `Inter`, and `M PLUS 1`.

The generated family is therefore named **Presevka**, not Pretendard or any
other Reserved Font Name.

## Generated font

The generated Presevka font is a Modified Version derived from OFL-licensed
font software and must remain under SIL OFL 1.1. The build copies the exact
Iosevka and Pretendard license files into `dist/licenses/` beside the font.

The MIT license in this repository's `LICENSE` applies only to the original
build scripts and documentation in this repository. It does not relicense the
generated font or either upstream font project.
