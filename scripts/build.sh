#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/weights.sh"
HINT_MODE="$(presevka_hint_mode)"

echo "Hinting mode: $HINT_MODE  (override with PRESEVKA_HINT=full|latin|gasp|none)"
"$ROOT/scripts/doctor.sh"
"$ROOT/scripts/build_iosevka.sh"
"$ROOT/scripts/build_pretendard.sh"
"$ROOT/scripts/merge.sh"

echo
echo "Build complete."
for weight in "${PRESEVKA_WEIGHTS[@]}"; do
  for slope in "${PRESEVKA_SLOPES[@]}"; do
    variant="$(presevka_variant_suffix "$weight" "$slope")"
    echo "  $ROOT/dist/Presevka-${variant}.ttf"
  done
done
