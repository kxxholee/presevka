#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/fonts/presevka"
shopt -s nullglob
fonts=("$ROOT"/dist/Presevka-*.ttf)
(( ${#fonts[@]} > 0 )) || { echo "Build the fonts first: ./scripts/build.sh" >&2; exit 1; }
mkdir -p "$DEST"
cp "${fonts[@]}" "$DEST/"
if command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f "$DEST"
fi
echo "Installed ${#fonts[@]} Presevka weights to $DEST"
