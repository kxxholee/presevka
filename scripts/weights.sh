#!/usr/bin/env bash

# Canonical static-weight order shared by every build stage.
readonly PRESEVKA_WEIGHTS=(
  Thin
  ExtraLight
  Light
  Regular
  Medium
  SemiBold
  Bold
  ExtraBold
  Black
)

declare -Ar PRESEVKA_WEIGHT_CLASSES=(
  [Thin]=100
  [ExtraLight]=200
  [Light]=300
  [Regular]=400
  [Medium]=500
  [SemiBold]=600
  [Bold]=700
  [ExtraBold]=800
  [Black]=900
)

# Upright and true Iosevka Italic faces. Pretendard Hangul remains upright in
# both faces because the upstream font does not provide an italic design.
readonly PRESEVKA_SLOPES=(
  Upright
  Italic
)

presevka_variant_suffix() {
  local weight="$1"
  local slope="$2"

  if [[ "$slope" == "Upright" ]]; then
    printf '%s\n' "$weight"
  elif [[ "$weight" == "Regular" ]]; then
    printf '%s\n' "$slope"
  else
    printf '%s%s\n' "$weight" "$slope"
  fi
}
