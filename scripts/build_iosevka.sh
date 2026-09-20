#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/weights.sh"
HINT_MODE="$(presevka_hint_mode)"
SRC="$ROOT/.cache/src/Iosevka"
OUT="$ROOT/build/iosevka"
REPO="${IOSEVKA_REPO:-https://github.com/be5invis/Iosevka.git}"
REF="${IOSEVKA_REF:-v34.8.0}"
JOBS="${IOSEVKA_JOBS:-2}"

[[ "$JOBS" =~ ^[1-9][0-9]*$ ]] || {
  echo "IOSEVKA_JOBS must be a positive integer; got $JOBS" >&2
  exit 1
}

mkdir -p "$ROOT/.cache/src" "$OUT"

if [[ ! -d "$SRC/.git" ]]; then
  git clone --depth 1 "$REPO" "$SRC"
fi

git -C "$SRC" fetch --depth 1 origin "$REF"
git -C "$SRC" checkout --detach FETCH_HEAD

cp "$ROOT/config/private-build-plans.toml" "$SRC/private-build-plans.toml"

(
  cd "$SRC"
  npm ci
  # Intentionally use the unhinted target. Presevka modifies/merges outlines
  # afterwards, so ttfautohint is neither required nor desirable here.
  npm run build -- ttf-unhinted::PresevkaBase500 "--jCmd=$JOBS"
)

for weight in "${PRESEVKA_WEIGHTS[@]}"; do
  for slope in "${PRESEVKA_SLOPES[@]}"; do
    variant="$(presevka_variant_suffix "$weight" "$slope")"
    source_font="$SRC/dist/PresevkaBase500/TTF-Unhinted/PresevkaBase500-${variant}.ttf"
    output_font="$OUT/Iosevka500-${variant}.ttf"

    if [[ ! -f "$source_font" ]]; then
      echo "Missing Iosevka ${weight} ${slope} output: $source_font" >&2
      echo "All generated TTFs:" >&2
      find "$SRC/dist/PresevkaBase500" -type f -iname '*.ttf' -print >&2 || true
      exit 1
    fi

    cp "$source_font" "$output_font"

    # In "latin" mode the Latin base is hinted here, before Hangul is merged in,
    # so ttfautohint never sees a Hangul outline. Every other mode either hints
    # the merged font or skips ttfautohint entirely.
    if [[ "$HINT_MODE" == "latin" ]]; then
      presevka_apply_hinting "$ROOT" autohint "$output_font"
    fi

    uv run python "$ROOT/tools/verify_iosevka.py" \
      "$output_font" \
      --weight-class "${PRESEVKA_WEIGHT_CLASSES[$weight]}" \
      --slope "$slope"
    echo "Iosevka base: $output_font"
  done
done
