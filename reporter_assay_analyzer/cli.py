from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from openpyxl import Workbook

from .mapping import write_mapping_template
from .io import parse_timepoint_hours, read_plate_matrix_xlsx
from .stacked_parser import parse_stacked_combined_raw_xlsx
from .analysis import analyze
from .plots import plot_by_condition


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="reporter_assay_analyzer",
        description="Reporter Assay Analyzer - NanoLuc plate time-course processing",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # make-template
    t = sub.add_parser("make-template", help="Generate a mapping template CSV (A1..H12).")
    t.add_argument("--out", required=True)

    # combine-raw
    c = sub.add_parser("combine-raw", help="Combine plate files into stacked Excel.")
    c.add_argument("--data-dir", required=True)
    c.add_argument("--out", required=True)

    # analyze
    a = sub.add_parser("analyze", help="Run final analysis.")
    a.add_argument("--combined", required=True)
    a.add_argument("--mapping", required=True)
    a.add_argument("--out", required=True)

    # plot
    pplot = sub.add_parser("plot", help="Generate plots (one per condition).")
    pplot.add_argument("--final", required=True)
    pplot.add_argument("--out-dir", required=True)
    pplot.add_argument(
        "--mode", choices=["fold", "reads"], default="fold",
        help="Plot fold-change or blank-subtracted reads",
    )

    # 🚀 run (NEW)
    r = sub.add_parser("run", help="Run full pipeline: combine → analyze → plot")
    r.add_argument("--data-dir", required=True)
    r.add_argument("--mapping", required=True)
    r.add_argument("--out-dir", required=True)
    r.add_argument(
        "--mode", choices=["fold", "reads"], default="fold",
        help="Plot fold-change or blank-subtracted reads",
    )

    return p


def _write_stacked_plates_excel(files: list[Path], out_path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "combined_raw"

    start_row = 1
    files = sorted(files, key=lambda p: parse_timepoint_hours(p.name))

    for f in files:
        t_h = parse_timepoint_hours(f.name)
        title = f"{t_h}h post transfection"
        plate = read_plate_matrix_xlsx(f)

        ws.cell(row=start_row, column=1, value=title)

        header_row = start_row + 1
        for j, col_num in enumerate(range(1, 13), start=2):
            ws.cell(row=header_row, column=j, value=col_num)

        for i, row_letter in enumerate("ABCDEFGH"):
            r = start_row + 2 + i
            ws.cell(row=r, column=1, value=row_letter)
            for j, col_num in enumerate(range(1, 13), start=2):
                val = plate.loc[row_letter, col_num]
                ws.cell(row=r, column=j, value=None if pd.isna(val) else float(val))

        start_row += 11

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "make-template":
        write_mapping_template(Path(args.out))
        print("✅ Mapping template written")
        return 0

    if args.command == "combine-raw":
        files = list(Path(args.data_dir).glob("*.xlsx"))
        _write_stacked_plates_excel(files, Path(args.out))
        print("✅ combined_raw.xlsx created")
        return 0

    if args.command == "analyze":
        tidy = parse_stacked_combined_raw_xlsx(Path(args.combined))
        mapping = pd.read_csv(args.mapping)
        result = analyze(tidy, mapping)
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        result.to_excel(args.out, index=False)
        print("✅ final_analysis.xlsx created")
        return 0

    if args.command == "plot":
        df = pd.read_excel(args.final)
        plot_by_condition(
            df,
            Path(args.out_dir),
            y_mode=args.mode,
            samples_order=["siNT", "siCIAO", "siFAM", "siMMS"],
        )
        print("✅ plots created")
        return 0

    # 🚀 RUN COMMAND
    if args.command == "run":
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        combined = out_dir / "combined_raw.xlsx"
        final = out_dir / "final_analysis.xlsx"
        plots_dir = out_dir / "plots"

        files = list(Path(args.data_dir).glob("*.xlsx"))
        _write_stacked_plates_excel(files, combined)

        tidy = parse_stacked_combined_raw_xlsx(combined)
        mapping = pd.read_csv(args.mapping)
        result = analyze(tidy, mapping)
        result.to_excel(final, index=False)

        plot_by_condition(
            result,
            plots_dir,
            y_mode=args.mode,
            samples_order=["siNT", "siCIAO", "siFAM", "siMMS"],
        )

        print("🚀 Full pipeline completed successfully")
        print(f"📄 {combined}")
        print(f"📊 {final}")
        print(f"📈 {plots_dir}")
        return 0

    parser.error("Unknown command")
    return 2
