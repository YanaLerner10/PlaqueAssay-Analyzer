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

🧠 Experimental Context

### This tool is designed for experiments with:

96-well plates

Quadruplicates per sample

Two conditions (e.g. 0 mM and 2 mM GuHCl)

Multiple timepoints, each exported as a separate file

Blank wells that receive substrate but no NanoLuc RNA

⚠️ Plate layout may differ between experiments — this is handled via a mapping template.

## 📥 Input
1️⃣ Plate reader files

Format: Excel (.xlsx)

One file per timepoint

Timepoint is parsed from the filename

### Example filenames:

0h post transfection.xlsx
1h post transfection.xlsx
2h post transfection.xlsx

## 2️⃣ Plate mapping template

A CSV or Excel file describing what each well represents.
You edit this once per experiment.

Required columns
Column	Description	Example
well	Well ID	B3
sample	Sample name	siNT, siFAM
condition	Experimental condition	0mM, 2mM
well_type	sample or blank	blank

🧪 Blank wells = no NanoLuc RNA, substrate only
Blank subtraction is performed per condition.

## 📤 Output
### 📄 1. Combined raw data

combined_raw.xlsx

All wells

All timepoints

No processing

Useful for QC and record keeping

### 📊 2. Final analysis

final_analysis.xlsx

For each sample × timepoint, the following columns are generated:

Column
0mM average
2mM average
blank
0mM minus blank
2mM minus blank
0mM (fold to siNT)
2mM (fold to siNT)

📌 Fold change is calculated relative to siNT at the same timepoint and condition.

### 📈 3. Time-course plots

One plot per siRNA

X-axis: hours post transfection

Y-axis: fold change to siNT

Separate curves for 0mM and 2mM

Saved as image files in the output directory.

## ⚙️ Installation
git clone <repository-url>
cd reporter-assay-analyzer

python -m venv .venv
  Windows
.venv\Scripts\activate
  macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

## 🚀 Usage
### Step 1 — Generate a mapping template
python -m reporter_assay_analyzer make-template \
  --out mapping_template.csv


Edit the template to match your plate layout.

### Step 2 — Run the analysis
python -m reporter_assay_analyzer run \
  --data-dir ./data/plates \
  --mapping ./mapping_template.csv \
  --out-dir ./output

## 🔬 Analysis Logic

For each timepoint:

Average technical replicates

Calculate blank signal per condition

Subtract blank from sample averages

Normalize to siNT (fold change)

All calculations are independent across timepoints.

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

Tests cover:

Timepoint parsing from filenames

Mapping file validation

Blank subtraction logic

Fold-change calculation

pytest

## 🔮 Future Improvements

CSV plate export support

Automatic plate block detection in raw Excel files

HTML summary reports

QC metrics (replicate CV, outlier detection)

## 🎓 Course Note

This project was developed as part of a Python programming course.
A link to the course repository will be added upon submission.
