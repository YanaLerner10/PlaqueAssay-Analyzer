import pandas as pd

from reporter_assay_analyzer.io import parse_timepoint_hours, _find_plate_block


def test_parse_timepoint_hours():
    assert parse_timepoint_hours("0h post transfection.xlsx") == 0
    assert parse_timepoint_hours("3h post transfection.xlsx") == 3
    assert parse_timepoint_hours("10h POST TRANSFECTION.xlsx") == 10


def test_find_plate_block_valid():
    """
    _find_plate_block expects a header row containing 1..12 and
    row labels A..H in the column immediately to the left of the 1..12 block.
    """
    # Build a minimal but VALID 8x12 plate-shaped layout inside a DataFrame.
    # Layout:
    # row 0: [None, 1, 2, ..., 12]
    # row 1..8: ["A", values...], ["B", values...], ... ["H", values...]
    header = [None] + list(range(1, 13))
    rows = [header]
    for i, r in enumerate("ABCDEFGH", start=1):
        rows.append([r] + [i * 10 + j for j in range(1, 13)])

    df = pd.DataFrame(rows)

    top_r, left_c = _find_plate_block(df)
    assert top_r == 0
    assert left_c == 1  # '1' starts at column index 1


def test_find_plate_block_invalid_small_plate():
    """
    A plate with fewer than 12 columns should not be detected.
    """
    df = pd.DataFrame({
        0: [None, "A", "B", "C", "D", "E", "F", "G", "H"],
        1: [1, 10, 20, 30, 40, 50, 60, 70, 80],
        2: [2, 11, 21, 31, 41, 51, 61, 71, 81],
    })

    try:
        _find_plate_block(df)
        assert False, "Expected ValueError for non-12-column plate header"
    except ValueError:
        assert True

