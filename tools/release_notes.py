from __future__ import annotations

import argparse
import re
from pathlib import Path

from font_utils import PRESEVKA_VERSION

# "### 20 September 2026 - Presevka 0.4.0 - Kwanho Lee (이관호)"
ENTRY = re.compile(r"^###\s+.*?\bPresevka\s+(?P<version>\d+\.\d+\.\d+)\b.*$", re.MULTILINE)

HEADER = """\
## 다운로드 / Downloads

| 파일 / File | 용도 / Use |
| --- | --- |
| `Presevka-{version}-ttf.zip` | 데스크톱 설치용, 9 weight × Upright/Italic 18개 페이스 / Desktop install, 18 faces |
| `Presevka-{version}-woff2.zip` | 웹폰트 / Web fonts |

개별 TTF 파일은 아래 자산 목록에서 따로 받을 수 있습니다.
Individual TTF faces are listed in the assets below.

라이선스 문서(`OFL.txt`, `THIRD_PARTY.md`, `FONTLOG.md`)는 각 아카이브에 함께 들어 있습니다.
Each archive ships with its licensing paperwork.

## 변경 사항 / Changes

{entry}
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Compose the release body from this version's FONTLOG entry."
    )
    p.add_argument("--version", default=PRESEVKA_VERSION)
    p.add_argument("--fontlog", type=Path, default=Path("FONTLOG.md"))
    p.add_argument("--output", type=Path)
    return p.parse_args()


def fontlog_entry(text: str, version: str) -> str:
    """Return the bullet list recorded in FONTLOG.md for one version."""
    matches = list(ENTRY.finditer(text))
    for index, match in enumerate(matches):
        if match.group("version") != version:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[match.end():end].strip()
    known = ", ".join(m.group("version") for m in matches) or "none"
    raise SystemExit(
        f"FONTLOG.md has no entry for {version}. Add one before releasing. "
        f"Entries found: {known}"
    )


def main() -> None:
    args = parse_args()
    entry = fontlog_entry(args.fontlog.read_text(encoding="utf-8"), args.version)
    body = HEADER.format(version=args.version, entry=entry)
    if args.output:
        args.output.write_text(body, encoding="utf-8")
        print(f"release notes: {args.output}")
    else:
        print(body, end="")


if __name__ == "__main__":
    main()
