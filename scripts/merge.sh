#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/weights.sh"
mkdir -p "$ROOT/dist/licenses"

for weight in "${PRESEVKA_WEIGHTS[@]}"; do
  base="$ROOT/build/iosevka/Iosevka432-${weight}.ttf"
  hangul="$ROOT/build/pretendard/Pretendard864-${weight}.ttf"
  output_font="$ROOT/dist/Presevka-${weight}.ttf"

  [[ -f "$base" ]] || { echo "Missing $base" >&2; exit 1; }
  [[ -f "$hangul" ]] || { echo "Missing $hangul" >&2; exit 1; }

  uv run python "$ROOT/tools/merge_fonts.py" \
    --base "$base" \
    --hangul "$hangul" \
    --output "$output_font" \
    --family "Presevka" \
    --style "$weight"

  uv run python "$ROOT/tools/qa_font.py" \
    "$output_font" \
    --family "Presevka" \
    --style "$weight" \
    --weight-class "${PRESEVKA_WEIGHT_CLASSES[$weight]}"
done

# Ship the exact upstream license texts beside the generated font.
cp "$ROOT/.cache/src/Iosevka/LICENSE.md" "$ROOT/dist/licenses/Iosevka-OFL-1.1.txt"
cp "$ROOT/.cache/src/pretendard/LICENSE" "$ROOT/dist/licenses/Pretendard-OFL-1.1.txt"
cp "$ROOT/OFL.txt" "$ROOT/dist/OFL.txt"
cp "$ROOT/THIRD_PARTY.md" "$ROOT/dist/THIRD_PARTY.md"
cp "$ROOT/FONTLOG.md" "$ROOT/dist/FONTLOG.md"

echo "Final fonts: $ROOT/dist/Presevka-*.ttf"
