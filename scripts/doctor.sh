#!/usr/bin/env bash
set -euo pipefail
missing=0
for cmd in git node npm uv; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%-6s %s\n' "$cmd" "$(command -v "$cmd")"
  else
    echo "MISSING: $cmd" >&2
    missing=1
  fi
done

if command -v node >/dev/null 2>&1; then
  node -e 'const major=Number(process.versions.node.split(".")[0]); if(major<18){console.error(`Node >=18 recommended; found ${process.versions.node}`); process.exit(1)} console.log(`node version ${process.versions.node} OK`)'
fi

if command -v uv >/dev/null 2>&1; then
  uv --version
fi

exit "$missing"
