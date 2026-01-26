# 🧪 Reporter Assay Analyzer

Automated analysis of time-course NanoLuc reporter assays from 96-well plate reader data

A Python tool that merges multiple plate-reader exports (one per timepoint), applies a flexible plate-mapping template, performs blank subtraction and normalization to control (siNT), and generates Excel result files and publication-ready time-course plots.

Designed for real virology lab workflows where analysis is usually done manually in Excel.

## ✨ Key Features

📁 Merge multiple plate-reader files into a single dataset

🧩 Flexible plate mapping (layout can change between experiments)

🔢 Automatic averaging of technical replicates (quadruplicates)

🚫 Blank subtraction (no NanoLuc + substrate only)

📊 Fold-change normalization to siNT control

📈 Time-course plots per siRNA and condition

📄 Clean Excel outputs for downstream analysis


## 📥 Input
1️⃣ Plate reader files

Format: Excel (.xlsx)

One file per timepoint, Timepoint is parsed from the filename

## 2️⃣ Plate mapping template

A CSV file describing what each well represents.
You edit this once per experiment.

Columns:
- `well` → e.g. A1, B6
- `sample` → e.g. siNT, siFAM, siMMS, siCIAO
- `condition` → `0mM`, `2mM`, or `all` (for shared blanks)
- `well_type` → `sample`, `blank`, or `unused`

Rules:
- Blank wells are marked as `well_type=blank` and `condition=all`
- Unused wells must be explicitly marked as `unused`
- Control sample name is **case-sensitive** (`siNT`)

An example mapping file is provided.

## 📤 Output

Running the full pipeline produces:

output/
├── combined_raw.xlsx # stacked 96-well plates (human-readable)
├── final_analysis.xlsx # fully processed analysis table
└── plots/
├── 0mM_timecourse.png
└── 2mM_timecourse.png


### `final_analysis.xlsx` includes:
- Replicate averages
- Shared blank value
- Blank-subtracted reads
- Fold-change relative to siNT
- Separate columns for 0 mM and 2 mM conditions

---

## ⚙️ Installation
git clone <repository-url>
cd reporter-assay-analyzer

python -m venv .venv
  Windows
.venv\Scripts\activate
  macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

### Requirements
- Python **3.11**
- Windows / macOS / Linux


## ⚡ Quickstart (recommended)

Run the entire pipeline with one command:

python -m reporter_assay_analyzer run \
  --data-dir data/plates \
  --mapping mapping_example.csv \
  --out-dir output \
  --mode fold

python -m reporter_assay_analyzer run --data-dir data/plates --mapping mapping_template.csv --out-dir output --mode fold


This will:

Combine all plate files into one Excel file

Perform full analysis (averaging, blank subtraction, normalization)

Generate time-course plots (one plot per condition)


## 🗂 Project Structure
reporter-assay-analyzer/
├── reporter_assay_analyzer/
│   ├── io.py        # file loading & timepoint parsing
│   ├── mapping.py   # plate mapping validation
│   ├── analysis.py  # calculations & normalization
│   ├── plots.py     # time-course plotting
│   └── cli.py       # command-line interface
├── tests/
├── data/
├── output/          # gitignored
├── requirements.txt
└── README.md

## 🧪 Testing

Run all tests with:

pytest

### Tests cover:

Timepoint extraction from filenames

Plate block detection

Parsing of stacked Excel plates

Correct fold-change normalization (siNT = 1)

## 🎓 Course Note

This project was developed as part of a Python programming course.
A link to the course repository will be added upon submission.
