#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="$ROOT/build/iosevka/Iosevka432-Regular.ttf"
HANGUL="$ROOT/build/pretendard/Pretendard-864.ttf"
OUT="$ROOT/dist/Presevka-Regular.ttf"

[[ -f "$BASE" ]] || { echo "Missing $BASE" >&2; exit 1; }
[[ -f "$HANGUL" ]] || { echo "Missing $HANGUL" >&2; exit 1; }
mkdir -p "$ROOT/dist/licenses"

uv run python "$ROOT/tools/merge_fonts.py" \
  --base "$BASE" \
  --hangul "$HANGUL" \
  --output "$OUT" \
  --family "Presevka" \
  --style "Regular"

uv run python "$ROOT/tools/qa_font.py" "$OUT" --family "Presevka"

# Ship the exact upstream license texts beside the generated font.
cp "$ROOT/.cache/src/Iosevka/LICENSE.md" "$ROOT/dist/licenses/Iosevka-OFL-1.1.txt"
cp "$ROOT/.cache/src/pretendard/LICENSE" "$ROOT/dist/licenses/Pretendard-OFL-1.1.txt"
cp "$ROOT/OFL.txt" "$ROOT/dist/OFL.txt"
cp "$ROOT/THIRD_PARTY.md" "$ROOT/dist/THIRD_PARTY.md"
cp "$ROOT/FONTLOG.md" "$ROOT/dist/FONTLOG.md"

echo "Final font: $OUT"
