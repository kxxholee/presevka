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

variants=()
for weight in "${PRESEVKA_WEIGHTS[@]}"; do
  for slope in "${PRESEVKA_SLOPES[@]}"; do
    variant="$(presevka_variant_suffix "$weight" "$slope")"
    [[ -f "$ROOT/dist/Presevka-${variant}.ttf" ]] || {
      echo "Missing $ROOT/dist/Presevka-${variant}.ttf. Run scripts/build.sh first." >&2
      exit 1
    }
    variants+=("$variant")
  done
done
expected=${#variants[@]}

# Brotli at its highest quality dominates packaging: roughly two minutes per
# face, serially. The faces are independent, so fan them out across cores.
presevka_woff2_one() {
  uv run python "$ROOT/tools/make_woff2.py" \
    --input "$ROOT/dist/Presevka-$1.ttf" \
    --output "$WOFF2_DIR/Presevka-$1.woff2"
}
export -f presevka_woff2_one
export ROOT WOFF2_DIR

jobs="${PRESEVKA_PACKAGE_JOBS:-$(nproc 2>/dev/null || echo 2)}"
printf '%s\n' "${variants[@]}" \
  | xargs -P "$jobs" -I{} bash -c 'presevka_woff2_one "$@"' _ {}

for variant in "${variants[@]}"; do
  [[ -f "$WOFF2_DIR/Presevka-${variant}.woff2" ]] || {
    echo "WOFF2 conversion failed for $variant" >&2
    exit 1
  }
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
