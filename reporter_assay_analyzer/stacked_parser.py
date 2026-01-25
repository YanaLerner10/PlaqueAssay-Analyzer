from __future__ import annotations

import re
from pathlib import Path
import pandas as pd

_TIME_RE = re.compile(r"(\d+)\s*h", re.IGNORECASE)


def parse_time_from_title(title: str) -> int:
    m = _TIME_RE.search(str(title))
    if not m:
        raise ValueError(f"Could not parse timepoint from title row: {title!r}")
    return int(m.group(1))


def parse_stacked_combined_raw_xlsx(path: Path, sheet_name: str = "combined_raw") -> pd.DataFrame:
    """
    Parse the 'stacked plates' combined_raw.xlsx (the pretty format you wanted)
    into tidy rows: time_h, well, value.

    Expected block format:
      Row 1: title like '0h post transfection'
      Row 2: header with 1..12 in columns B..M
      Rows 3-10: A..H in column A, values in B..M
      Optional: 'Lum' label column N
      Row 11: blank spacer
      Then repeats
    """
    df = pd.read_excel(path, sheet_name=sheet_name, header=None, engine="openpyxl")

    rows = []
    r = 0
    n = df.shape[0]

    while r < n:
        title = df.iloc[r, 0]
        if pd.isna(title):
            r += 1
            continue

        # detect a block by checking the next row has 1..12 in columns 1..12 (B..M)
        header = df.iloc[r + 1, 1:13].tolist() if r + 1 < n else []
        try:
            header_norm = [int(x) for x in header]
        except Exception:
            header_norm = []

        if header_norm != list(range(1, 13)):
            r += 1
            continue

        time_h = parse_time_from_title(str(title))

        # rows A..H
        for i, row_letter in enumerate("ABCDEFGH"):
            rr = r + 2 + i
            if rr >= n:
                break
            label = str(df.iloc[rr, 0]).strip().upper()
            if label != row_letter:
                # layout mismatch; skip block safely
                continue

            values = df.iloc[rr, 1:13].tolist()  # B..M
            for col_idx, val in enumerate(values, start=1):
                well = f"{row_letter}{col_idx}"
                value = pd.to_numeric(val, errors="coerce")
                rows.append({"time_h": time_h, "well": well, "value": value})

        # jump to next block (title row of next block)
        r = r + 11

    if not rows:
        raise ValueError(
            "Parsed 0 rows from combined_raw.xlsx. "
            "Make sure the file is the stacked-plates format and the sheet name is 'combined_raw'."
        )

    tidy = pd.DataFrame(rows).sort_values(["time_h", "well"]).reset_index(drop=True)
    return tidy
