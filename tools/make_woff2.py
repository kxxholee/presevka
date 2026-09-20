from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.ttLib import TTFont


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert a built TTF to WOFF2.")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    font = TTFont(args.input)
    try:
        font.flavor = "woff2"
        font.save(args.output)
    finally:
        font.close()
    ratio = args.output.stat().st_size / args.input.stat().st_size
    print(f"woff2: {args.output} ({ratio:.0%} of TTF)")


if __name__ == "__main__":
    main()
