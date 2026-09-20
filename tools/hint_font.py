from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram

# Grid-fit + grayscale + both symmetric ClearType bits, for every size. This is
# the value ttfautohint itself writes, so all hinting modes agree on it.
GASP_ALL_SIZES = 0x0F

# Dropout control, so thin stems survive at small sizes in a font that carries
# no per-glyph instructions.
SMOOTH_PREP = """
PUSHW[ ]
511
SCANCTRL[ ]
PUSHB[ ]
4
SCANTYPE[ ]
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Apply the requested hinting stage to a built font."
    )
    p.add_argument(
        "action",
        choices=("autohint", "smooth"),
        help=(
            "autohint: run ttfautohint (it writes its own gasp table). "
            "smooth: add only a gasp table and dropout-control prep program."
        ),
    )
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    return p.parse_args()


def autohint(src: Path, dst: Path) -> None:
    from ttfautohint import ttfautohint

    # no_info is required: by default ttfautohint appends its own version and
    # options to name ID 5, which qa_font.py compares for exact equality.
    data = ttfautohint(in_file=str(src), no_info=True)
    dst.write_bytes(data)


def smooth(src: Path, dst: Path) -> None:
    font = TTFont(src)
    try:
        if "gasp" not in font:
            font["gasp"] = newTable("gasp")
        font["gasp"].version = 1
        font["gasp"].gaspRange = {65535: GASP_ALL_SIZES}

        program = ttProgram.Program()
        program.fromAssembly(SMOOTH_PREP)
        if "prep" not in font:
            font["prep"] = newTable("prep")
        font["prep"].program = program

        # An unhinted font reports a zero-depth stack; the prep program above
        # needs room to push its arguments.
        maxp = font["maxp"]
        maxp.maxStackElements = max(maxp.maxStackElements, 8)

        font.save(dst)
    finally:
        font.close()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.action == "autohint":
        autohint(args.input, args.output)
    else:
        smooth(args.input, args.output)
    print(f"{args.action}: {args.output}")


if __name__ == "__main__":
    main()
