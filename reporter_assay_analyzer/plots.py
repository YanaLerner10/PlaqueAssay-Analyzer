from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def make_timecourse_plots(final_df: pd.DataFrame, out_dir: Path) -> None:
    """
    Create one plot per sample: fold-change vs time, with 0mM and 2mM curves.

    Accepts multiple possible column naming conventions.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # Required base columns
    if "time_h" not in final_df.columns or "sample" not in final_df.columns:
        raise ValueError("final_df must include columns: 'time_h' and 'sample'")

    # Fold-change column candidates (support both naming styles)
    col_0mM = _find_col(final_df, ["0mM (fold to siNT)", "fold_to_siNT_0mM", "fold_to_siNT_0"])
    col_2mM = _find_col(final_df, ["2mM (fold to siNT)", "fold_to_siNT_2mM", "fold_to_siNT_2"])

    if not col_0mM or not col_2mM:
        raise ValueError(
            "Could not find fold-change columns for 0mM/2mM.\n"
            f"Columns available: {list(final_df.columns)}\n"
            "Expected columns like '0mM (fold to siNT)' and '2mM (fold to siNT)'."
        )

    df = final_df.copy()
    df["time_h"] = pd.to_numeric(df["time_h"], errors="coerce")
    df = df.sort_values(["sample", "time_h"])

    for sample, sdf in df.groupby("sample"):
        x = sdf["time_h"].tolist()
        y0 = pd.to_numeric(sdf[col_0mM], errors="coerce").tolist()
        y2 = pd.to_numeric(sdf[col_2mM], errors="coerce").tolist()

        plt.figure()
        plt.plot(x, y0, marker="o", label="0mM")
        plt.plot(x, y2, marker="o", label="2mM")
        plt.xlabel("Hours post transfection")
        plt.ylabel("Fold change to siNT")
        plt.title(sample)
        plt.legend()
        plt.tight_layout()

        safe_name = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in str(sample))
        plt.savefig(out_dir / f"{safe_name}_timecourse.png", dpi=200)
        plt.close()
