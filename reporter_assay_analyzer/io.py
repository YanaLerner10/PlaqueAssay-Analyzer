from __future__ import annotations

import re
from pathlib import Path
import pandas as pd


_TIME_RE = re.compile(r"(\d+)\s*h", re.IGNORECASE)


def parse_timepoint_hours(filename: str) -> int:
    """
    Extract timepoint in hours from filename like:
    '0h post transfection.xlsx' -> 0
    '3h post transfection.xlsx' -> 3
    """
    m = _TIME_RE.search(filename)
    if not m:
        raise ValueError(f"Could not parse timepoint (e.g. '3h') from filename: {filename}")
    return int(m.group(1))


def _find_plate_block(df: pd.DataFrame) -> tuple[int, int]:
    """
    Try to locate the top-left corner of an 8x12 plate matrix in a messy Excel sheet.

    Expected layout somewhere in the sheet:
      header row contains 1..12
      first column contains A..H
      values in the 8x12 block are numeric

    Returns:
      (top_row_index, left_col_index) where:
        df.iloc[top_row_index, left_col_index] == 1
        and df.iloc[top_row_index+1:top_row_index+9, left_col_index-1] == A..H
    """
    # brute-force scan: look for a row containing 1..12 (as ints or strings)
    for r in range(df.shape[0]):
        row = df.iloc[r, :].tolist()
        # find potential start col where 1..12 appear consecutively
        for c in range(df.shape[1] - 11):
            chunk = row[c : c + 12]
            norm = []
            for x in chunk:
                if pd.isna(x):
                    norm.append(None)
                else:
                    s = str(x).strip()
                    # allow "1", 1, "1.0"
                    try:
                        norm.append(int(float(s)))
                    except Exception:
                        norm.append(None)
            if norm == list(range(1, 13)):
                # check row labels directly to the left (c-1) in the next 8 rows
                if c - 1 < 0:
                    continue
                labels = df.iloc[r + 1 : r + 9, c - 1].tolist()
                labels = [str(x).strip().upper() if not pd.isna(x) else "" for x in labels]
                if labels == list("ABCDEFGH"):
                    return r, c

    raise ValueError(
        "Could not locate the 8x12 plate block (A-H rows, 1-12 columns) in the Excel file. "
        "If your export format changed, we can adjust the detector."
    )


def read_plate_xlsx(path: Path) -> pd.DataFrame:
    """
    Read one plate export (xlsx) and return tidy data:
      columns: well, value
    """
    raw = pd.read_excel(path, header=None, engine="openpyxl")
    top_r, left_c = _find_plate_block(raw)

    # plate values are in rows A..H => top_r+1 .. top_r+8, cols 1..12 => left_c .. left_c+11
    block = raw.iloc[top_r + 1 : top_r + 9, left_c : left_c + 12].copy()
    block.index = list("ABCDEFGH")
    block.columns = list(range(1, 13))

    tidy = (
    block.stack()
    .reset_index()
    .rename(columns={"level_0": "row", "level_1": "col", 0: "value"})
)
    tidy["well"] = tidy["row"].astype(str) + tidy["col"].astype(str)
    tidy = tidy[["well", "value"]]

    # enforce numeric where possible
    tidy["value"] = pd.to_numeric(tidy["value"], errors="coerce")
    return tidy
def read_plate_matrix_xlsx(path: Path) -> pd.DataFrame:
    """
    Read one plate export (xlsx) and return an 8x12 matrix:
      index: A..H
      columns: 1..12
    """
    raw = pd.read_excel(path, header=None, engine="openpyxl")
    top_r, left_c = _find_plate_block(raw)

    block = raw.iloc[top_r + 1 : top_r + 9, left_c : left_c + 12].copy()
    block.index = list("ABCDEFGH")
    block.columns = list(range(1, 13))

    # numeric conversion
    block = block.apply(pd.to_numeric, errors="coerce")
    return block

