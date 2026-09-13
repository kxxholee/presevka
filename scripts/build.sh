#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/weights.sh"

"$ROOT/scripts/doctor.sh"
"$ROOT/scripts/build_iosevka.sh"
"$ROOT/scripts/build_pretendard.sh"
"$ROOT/scripts/merge.sh"

echo
echo "Build complete."
for weight in "${PRESEVKA_WEIGHTS[@]}"; do
  echo "  $ROOT/dist/Presevka-${weight}.ttf"
done
