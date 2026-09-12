#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT/scripts/doctor.sh"
"$ROOT/scripts/build_iosevka.sh"
"$ROOT/scripts/build_pretendard.sh"
"$ROOT/scripts/merge.sh"

echo
echo "Build complete."
echo "  $ROOT/dist/Presevka-Regular.ttf"
