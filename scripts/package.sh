#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/weights.sh"

VERSION="$(PYTHONPATH="$ROOT/tools" uv run python -c \
  'import font_utils; print(font_utils.PRESEVKA_VERSION)')"
STAGE="$ROOT/build/package"
WOFF2_DIR="$ROOT/dist/woff2"

rm -rf "$STAGE" "$ROOT/dist"/Presevka-*.zip
mkdir -p "$WOFF2_DIR"

expected=0
for weight in "${PRESEVKA_WEIGHTS[@]}"; do
  for slope in "${PRESEVKA_SLOPES[@]}"; do
    variant="$(presevka_variant_suffix "$weight" "$slope")"
    ttf="$ROOT/dist/Presevka-${variant}.ttf"
    [[ -f "$ttf" ]] || { echo "Missing $ttf. Run scripts/build.sh first." >&2; exit 1; }
    uv run python "$ROOT/tools/make_woff2.py" \
      --input "$ttf" --output "$WOFF2_DIR/Presevka-${variant}.woff2"
    expected=$((expected + 1))
  done
done

# Both archives carry the same licensing paperwork as the loose fonts.
stage_docs() {
  local dest="$1"
  mkdir -p "$dest/licenses"
  cp "$ROOT/OFL.txt" "$ROOT/THIRD_PARTY.md" "$ROOT/FONTLOG.md" "$dest/"
  cp "$ROOT/dist/licenses/"*.txt "$dest/licenses/"
}

mkdir -p "$STAGE/ttf/Presevka-$VERSION" "$STAGE/woff2/Presevka-$VERSION"
cp "$ROOT/dist"/Presevka-*.ttf "$STAGE/ttf/Presevka-$VERSION/"
cp "$WOFF2_DIR"/Presevka-*.woff2 "$STAGE/woff2/Presevka-$VERSION/"
stage_docs "$STAGE/ttf/Presevka-$VERSION"
stage_docs "$STAGE/woff2/Presevka-$VERSION"

(cd "$STAGE/ttf" && zip -qr9 "$ROOT/dist/Presevka-$VERSION-ttf.zip" "Presevka-$VERSION")
(cd "$STAGE/woff2" && zip -qr9 "$ROOT/dist/Presevka-$VERSION-woff2.zip" "Presevka-$VERSION")
rm -rf "$STAGE"

echo
echo "Packaged $expected faces at version $VERSION:"
for archive in "$ROOT/dist/Presevka-$VERSION"-{ttf,woff2}.zip; do
  printf '  %s (%s)\n' "$archive" "$(du -h "$archive" | cut -f1)"
done
