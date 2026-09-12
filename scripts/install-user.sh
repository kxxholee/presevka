#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FONT="$ROOT/dist/Presevka-Regular.ttf"
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/fonts/presevka"
[[ -f "$FONT" ]] || { echo "Build the font first: ./scripts/build.sh" >&2; exit 1; }
mkdir -p "$DEST"
cp "$FONT" "$DEST/"
if command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f "$DEST"
fi
echo "Installed to $DEST"
