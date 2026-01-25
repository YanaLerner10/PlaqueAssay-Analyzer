import pandas as pd
from reporter_assay_analyzer.analysis import analyze


def test_analyze_produces_fold_columns():
    # tidy: two timepoints, 4 wells only (enough to test logic)
    tidy = pd.DataFrame({
        "time_h": [0, 0, 0, 0, 1, 1, 1, 1],
        "well":   ["A1", "A2", "A6", "B6", "A1", "A2", "A6", "B6"],
        "value":  [100, 200, 10, 10,  110, 220, 10, 10],
    })

    # mapping:
    # A1 = siNT 0mM sample
    # A2 = siFAM 0mM sample
    # A6,B6 = blank wells (shared)
    mapping = pd.DataFrame({
        "well": ["A1", "A2", "A6", "B6"],
        "sample": ["siNT", "siFAM", "blank", "blank"],
        "condition": ["0mM", "0mM", "all", "all"],
        "well_type": ["sample", "sample", "blank", "blank"],
    })

    out = analyze(tidy, mapping)

    assert "0mM (fold to siNT)" in out.columns
    # siNT fold should be 1 (minus_blank / minus_blank)
    nt_rows = out[out["sample"] == "siNT"]
    assert all(abs(x - 1.0) < 1e-9 for x in nt_rows["0mM (fold to siNT)"].dropna())
