#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/.cache/src/pretendard"
OUT="$ROOT/build/pretendard"
REPO="${PRETENDARD_REPO:-https://github.com/orioncactus/pretendard.git}"
REF="${PRETENDARD_REF:-v1.3.9}"
BASE="$ROOT/build/iosevka/Iosevka432-Regular.ttf"

[[ -f "$BASE" ]] || { echo "Missing Iosevka base. Run scripts/build_iosevka.sh first." >&2; exit 1; }
mkdir -p "$ROOT/.cache/src" "$OUT"

if [[ ! -d "$SRC/.git" ]]; then
  git clone --depth 1 "$REPO" "$SRC"
fi

git -C "$SRC" fetch --depth 1 origin "$REF"
git -C "$SRC" checkout --detach FETCH_HEAD

# Official Pretendard repository path as of v1.3.x/main.
FONT="$SRC/packages/pretendard/dist/public/static/Pretendard-Regular.otf"

# Keep a conservative fallback in case upstream reorganizes the distribution.
if [[ ! -f "$FONT" ]]; then
  mapfile -t candidates < <(
    find "$SRC" -type f \( -iname 'Pretendard-Regular.otf' -o -iname 'Pretendard-Regular.ttf' \) \
      | grep -Ev '/node_modules/' \
      | sort -u
  )
  if (( ${#candidates[@]} != 1 )); then
    echo "Could not uniquely identify Pretendard Regular." >&2
    printf 'Candidates (%d):\n' "${#candidates[@]}" >&2
    printf '  %s\n' "${candidates[@]:-<none>}" >&2
    exit 1
  fi
  FONT="${candidates[0]}"
fi

uv run python "$ROOT/tools/prepare_pretendard.py" \
  --input "$FONT" \
  --base-font "$BASE" \
  --output "$OUT/Pretendard-864.ttf" \
  --report "$OUT/Pretendard-864.metrics.json"

echo "Pretendard donor: $OUT/Pretendard-864.ttf"
