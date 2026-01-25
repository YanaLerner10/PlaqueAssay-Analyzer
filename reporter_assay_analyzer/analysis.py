from __future__ import annotations

import pandas as pd

CONTROL_SAMPLE = "siNT"


def _standardize_condition(series: pd.Series) -> pd.Series:
    # turn things like "0 mM", "0MM", "2mM " into exactly "0mM"/"2mM"
    s = series.astype(str).str.strip().str.lower()
    s = s.str.replace(" ", "", regex=False)

    s = s.replace({
        "0": "0mM",
        "0mm": "0mM",
        "0mmguhcl": "0mM",
        "0mmg": "0mM",
        "2": "2mM",
        "2mm": "2mM",
        "2mmguhcl": "2mM",
        "2mmg": "2mM",
    })
    # keep original if already fine, otherwise it stays as-is
    # but we want exact casing:
    s = s.replace({"0mm": "0mM", "2mm": "2mM"})
    return s


def analyze(tidy: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    """
    Inputs:
      tidy: time_h, well, value
      mapping: well, sample, condition, well_type

    Behavior:
      - blanks are shared (one blank per timepoint)
      - blank = mean of all wells with well_type='blank' per timepoint
      - average replicates per sample+condition+time
      - subtract blank
      - fold change to siNT per timepoint+condition:
          (sample minus blank) / (siNT minus blank)

    Output columns:
      time_h, sample,
      0mM average, 2mM average,
      blank, 0mM blank, 2mM blank,
      0mM minus blank, 2mM minus blank,
      0mM (fold to siNT), 2mM (fold to siNT)
    """
    required = {"well", "sample", "condition", "well_type"}
    if not required.issubset(mapping.columns):
        raise ValueError(f"Mapping file must include columns: {sorted(required)}")

    df = tidy.merge(mapping, on="well", how="left")

    # Ensure every well is mapped (no NaNs)
    if df["sample"].isna().any():
        missing = sorted(df.loc[df["sample"].isna(), "well"].unique().tolist())
        raise ValueError(f"Unmapped wells found in mapping file: {missing}")

    # Normalize strings
    df["well_type"] = df["well_type"].astype(str).str.strip().str.lower()
    df["sample"] = df["sample"].astype(str).str.strip()
    df["condition"] = _standardize_condition(df["condition"])

    blanks_df = df[df["well_type"] == "blank"].copy()
    samples_df = df[df["well_type"] == "sample"].copy()

    # 1) shared blank per timepoint
    blanks = (
        blanks_df.groupby("time_h", dropna=False)
        .agg(blank=("value", "mean"))
        .reset_index()
    )

    # 2) replicate mean per time/sample/condition
    samples = (
        samples_df.groupby(["time_h", "sample", "condition"], dropna=False)
        .agg(mean_value=("value", "mean"))
        .reset_index()
        .merge(blanks, on="time_h", how="left")
    )
    samples["minus_blank"] = samples["mean_value"] - samples["blank"]

    # 3) fold to siNT per time+condition
    control = (
        samples[samples["sample"] == CONTROL_SAMPLE]
        .rename(columns={"minus_blank": "control_minus_blank"})
        [["time_h", "condition", "control_minus_blank"]]
    )
    samples = samples.merge(control, on=["time_h", "condition"], how="left")
    samples["fold_to_siNT"] = samples["minus_blank"] / samples["control_minus_blank"]

    # 4) Build wide output WITHOUT pivot (guarantees columns exist)
    def pack(cond: str) -> pd.DataFrame:
        sub = samples[samples["condition"] == cond][
            ["time_h", "sample", "mean_value", "minus_blank", "fold_to_siNT"]
        ].copy()
        sub = sub.rename(
            columns={
                "mean_value": f"{cond} average",
                "minus_blank": f"{cond} minus blank",
                "fold_to_siNT": f"{cond} (fold to siNT)",
            }
        )
        return sub

    wide = pack("0mM").merge(pack("2mM"), on=["time_h", "sample"], how="outer")
    wide = wide.merge(blanks, on="time_h", how="left")
    wide["0mM blank"] = wide["blank"]
    wide["2mM blank"] = wide["blank"]

    # nice ordering
    desired = [
        "time_h", "sample",
        "0mM average", "2mM average",
        "blank", "0mM blank", "2mM blank",
        "0mM minus blank", "2mM minus blank",
        "0mM (fold to siNT)", "2mM (fold to siNT)",
    ]
    cols = [c for c in desired if c in wide.columns] + [c for c in wide.columns if c not in desired]
    wide = wide[cols].sort_values(["time_h", "sample"]).reset_index(drop=True)

    return wide
