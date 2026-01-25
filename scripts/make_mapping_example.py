from __future__ import annotations

import csv
from pathlib import Path

ROWS = "ABCDEFGH"
COLS = range(1, 13)

# Example layout (EDIT if you want):
# - Column 6 is blank wells for ALL conditions (shared blank)
# - Columns 1-5 are 0mM samples (quadruplicates in rows A-D)
# - Columns 7-11 are 2mM samples (quadruplicates in rows A-D)
#
# Samples: siNT, siFAM, siMMS, siCIAO
# We’ll map 4 replicates per sample per condition using a simple pattern:
# A-D rows used, E-H unused

SAMPLES = ["siNT", "siFAM", "siMMS", "siCIAO"]


def well(r: str, c: int) -> str:
    return f"{r}{c}"


def main() -> None:
    out = Path("mapping_example.csv")

    # start with everything unused
    mapping = {}
    for r in ROWS:
        for c in COLS:
            w = well(r, c)
            mapping[w] = {"well": w, "sample": "unused", "condition": "unused", "well_type": "unused"}

    # blanks in column 6 (all rows)
    for r in ROWS:
        w = well(r, 6)
        mapping[w] = {"well": w, "sample": "blank", "condition": "all", "well_type": "blank"}

    # helper to assign 4 replicates in rows A-D for a given column
    def assign_replicates(col: int, condition: str) -> None:
        # rows A-D hold 4 samples, one per row for simplicity
        # (you can change this to match your real plate layout)
        for i, r in enumerate("ABCD"):
            sample = SAMPLES[i]
            w = well(r, col)
            mapping[w] = {"well": w, "sample": sample, "condition": condition, "well_type": "sample"}

    # 0mM in columns 1-5
    for c in range(1, 6):
        assign_replicates(c, "0mM")

    # 2mM in columns 7-11
    for c in range(7, 12):
        assign_replicates(c, "2mM")

    # write CSV
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["well", "sample", "condition", "well_type"])
        writer.writeheader()
        for r in ROWS:
            for c in COLS:
                writer.writerow(mapping[well(r, c)])

    print(f"✅ Wrote {out.resolve()}")
    print("Edit scripts/make_mapping_example.py if you want the example layout to match your real plate more closely.")


if __name__ == "__main__":
    main()
