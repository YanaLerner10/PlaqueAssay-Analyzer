from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


ROWS = list("ABCDEFG")
COLS = list(range(1, 13))


def iter_wells() -> Iterable[str]:
    for r in ROWS:
        for c in COLS:
            yield f"{r}{c}"


def write_mapping_template(out_path: Path) -> None:
    """
    Write a CSV template with one row per well (A1..H12).

    Columns:
      - well: well id (e.g., B3)
      - sample: user fills (e.g., siNT)
      - condition: user fills (0mM/2mM)
      - well_type: user fills (sample/blank)
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["well", "sample", "condition", "well_type"]
        )
        writer.writeheader()
        for well in iter_wells():
            writer.writerow(
                {"well": well, "sample": "", "condition": "", "well_type": ""}
            )
