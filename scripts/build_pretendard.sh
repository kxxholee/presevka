#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/weights.sh"
SRC="$ROOT/.cache/src/pretendard"
OUT="$ROOT/build/pretendard"
REPO="${PRETENDARD_REPO:-https://github.com/orioncactus/pretendard.git}"
REF="${PRETENDARD_REF:-v1.3.9}"
mkdir -p "$ROOT/.cache/src" "$OUT"

if [[ ! -d "$SRC/.git" ]]; then
  git clone --depth 1 "$REPO" "$SRC"
fi

git -C "$SRC" fetch --depth 1 origin "$REF"
git -C "$SRC" checkout --detach FETCH_HEAD

for weight in "${PRESEVKA_WEIGHTS[@]}"; do
  base="$ROOT/build/iosevka/Iosevka480-${weight}.ttf"
  font="$SRC/packages/pretendard/dist/public/static/Pretendard-${weight}.otf"
  output_font="$OUT/Pretendard960-${weight}.ttf"
  report="$OUT/Pretendard960-${weight}.metrics.json"

  [[ -f "$base" ]] || {
    echo "Missing Iosevka ${weight} base. Run scripts/build_iosevka.sh first." >&2
    exit 1
  }

  # Keep a conservative fallback in case upstream reorganizes the distribution.
  if [[ ! -f "$font" ]]; then
    mapfile -t candidates < <(
      find "$SRC" -type f \
        \( -iname "Pretendard-${weight}.otf" -o -iname "Pretendard-${weight}.ttf" \) \
        | grep -Ev '/node_modules/' \
        | sort -u
    )
    if (( ${#candidates[@]} != 1 )); then
      echo "Could not uniquely identify Pretendard ${weight}." >&2
      printf 'Candidates (%d):\n' "${#candidates[@]}" >&2
      printf '  %s\n' "${candidates[@]:-<none>}" >&2
      exit 1
    fi
    font="${candidates[0]}"
  fi

  uv run python "$ROOT/tools/prepare_pretendard.py" \
    --input "$font" \
    --base-font "$base" \
    --output "$output_font" \
    --report "$report"

  echo "Pretendard donor: $output_font"
done
