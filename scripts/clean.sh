#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rm -rf "$ROOT/build" "$ROOT/dist"
mkdir -p "$ROOT/build" "$ROOT/dist"
# dist/.gitkeep is tracked; recreate it so a clean does not dirty the tree.
touch "$ROOT/dist/.gitkeep"
echo "Removed generated build/dist files. .cache/src is kept to avoid re-cloning."
