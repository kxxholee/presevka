#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/.cache/src/Iosevka"
OUT="$ROOT/build/iosevka"
REPO="${IOSEVKA_REPO:-https://github.com/be5invis/Iosevka.git}"
REF="${IOSEVKA_REF:-v34.8.0}"

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
  npm run build -- ttf-unhinted::PresevkaBase432
)

mapfile -t candidates < <(
  find "$SRC/dist/PresevkaBase432/TTF-Unhinted" -type f -iname '*.ttf' 2>/dev/null \
    | grep -Ei 'regular' \
    | grep -Evi 'italic|oblique' \
    | sort
)

if (( ${#candidates[@]} != 1 )); then
  echo "Could not uniquely identify the Regular Upright Iosevka build." >&2
  printf 'Candidates (%d):\n' "${#candidates[@]}" >&2
  printf '  %s\n' "${candidates[@]:-<none>}" >&2
  echo "All generated TTFs:" >&2
  find "$SRC/dist/PresevkaBase432" -type f -iname '*.ttf' -print >&2 || true
  exit 1
fi

cp "${candidates[0]}" "$OUT/Iosevka432-Regular.ttf"
uv run python "$ROOT/tools/verify_iosevka.py" "$OUT/Iosevka432-Regular.ttf"
echo "Iosevka base: $OUT/Iosevka432-Regular.ttf"
