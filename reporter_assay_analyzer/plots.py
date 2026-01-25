from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def plot_by_condition(
    final_df: pd.DataFrame,
    out_dir: Path,
    y_mode: str = "fold",   # "fold" or "reads"
    samples_order: list[str] | None = None,
) -> None:
    """
    Create 2 plots: one for 0mM and one for 2mM.
    Each plot shows multiple samples as lines over time.

    final_df: wide table with columns like:
      - time_h, sample
      - 0mM minus blank, 2mM minus blank
      - 0mM (fold to siNT), 2mM (fold to siNT)

    y_mode:
      - "fold"  -> uses 'XmM (fold to siNT)'
      - "reads" -> uses 'XmM minus blank'
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    if "time_h" not in final_df.columns or "sample" not in final_df.columns:
        raise ValueError("final_df must include 'time_h' and 'sample' columns")

    df = final_df.copy()
    df["time_h"] = pd.to_numeric(df["time_h"], errors="coerce")

    if y_mode not in {"fold", "reads"}:
        raise ValueError("y_mode must be 'fold' or 'reads'")

    if y_mode == "fold":
        col_0 = "0mM (fold to siNT)"
        col_2 = "2mM (fold to siNT)"
        ylabel = "Fold change to siNT"
        title_suffix = " (fold to siNT)"
    else:
        col_0 = "0mM minus blank"
        col_2 = "2mM minus blank"
        ylabel = "Reads (blank-subtracted)"
        title_suffix = " (blank-subtracted reads)"

    missing_cols = [c for c in [col_0, col_2] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns for plotting: {missing_cols}. "
                         f"Available columns: {list(df.columns)}")

    # Determine which samples to plot
    present_samples = sorted(df["sample"].dropna().unique().tolist())
    if samples_order is None:
        # default: siNT first, then others alphabetically
        samples_order = ["siNT"] + [s for s in present_samples if s != "siNT"]
    # keep only those that exist
    samples_order = [s for s in samples_order if s in present_samples]

    def make_one(cond_label: str, y_col: str, out_name: str) -> None:
        # Build a wide plotting frame: index=time_h, columns=sample
        plot_df = df.pivot_table(index="time_h", columns="sample", values=y_col, aggfunc="first")
        plot_df = plot_df.sort_index()

        plt.figure()

        # plot in the requested order
        for s in samples_order:
            if s in plot_df.columns:
                plt.plot(plot_df.index, plot_df[s], marker="o", label=s)

        plt.xlabel("Hours post transfection")
        plt.ylabel(ylabel)
        plt.title(f"{cond_label}{title_suffix}")
        plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.3), ncol=4, frameon=False)
        plt.tight_layout()

        plt.savefig(out_dir / out_name, dpi=200, bbox_inches="tight")
        plt.close()

    make_one("0mM", col_0, "0mM_timecourse.png")
    make_one("2mM", col_2, "2mM_timecourse.png")
