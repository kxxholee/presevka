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
