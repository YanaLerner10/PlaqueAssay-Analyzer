# PlaqueAssay-Analyzer

## Short description
PlaqueAssay-Analyzer is a Streamlit-based Python application that automates the analysis of viral plaque assays from scanned TIFF images.  
The tool counts plaques from single-well images, generates quality-control overlay images, and calculates viral titers (PFU/mL) in a reproducible and transparent way.

---

## Why is this project interesting to me?
Plaque assays are a routine but time-consuming part of my research workflow.  
Currently, plaque counting is performed manually using ImageJ, followed by separate calculations in spreadsheets. This process is repetitive, prone to human error, and difficult to standardize between experiments.

This project is interesting and useful to me because it:
- Automates a real and frequent lab task
- Reduces manual work and calculation errors
- Produces consistent, reproducible outputs
- Can realistically be used beyond this course in my research

---

## What does this project do?
The application provides an end-to-end plaque assay analysis workflow:

1. Accepts scanned TIFF images of individual wells (white plaques on dark background)
2. Allows the user to define experimental metadata (sample, dilution, replicate)
3. Automatically detects and counts plaques using image processing
4. Generates overlay images for quality control
5. Calculates PFU/mL values and summary statistics
6. Outputs results as tables and plots

The project is designed to work even when image filenames are inconsistent, by relying on a user-edited manifest table rather than file naming conventions.

---

## Input
The project expects the following input:

### 1. Image data
- A ZIP file containing `.tif` or `.tiff` images
- Each image corresponds to a single well from a 6-well plaque assay plate
- Plaques are expected to appear as white spots on a dark background

### 2. Manifest table (created within the app)
A table containing experimental metadata for each image, including:
- Image file name
- Sample name
- Dilution factor (e.g. `1e-5`)
- Replicate number
- Plated volume (default: 0.1 mL)

---

## Output
The application produces the following outputs:

- `manifest.csv` – the finalized metadata table
- `counts.csv` – plaque counts per image with quality-control metrics
- Overlay images showing detected plaques outlined on the original image
- `results.csv` – calculated PFU/mL values per replicate and summary statistics (mean ± SD)
- Plots visualizing viral titers and replicate variability

---

## Requirements
- Python 3.11
- The following Python packages:
  - streamlit
  - opencv-python
  - numpy
  - pandas
  - matplotlib
  - pillow

All dependencies are listed in `requirements.txt`.

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/PlaqueAssay-Analyzer.git
   cd PlaqueAssay-Analyzer
2. Create and activate a virtual environment (Windows example):

py -3.11 -m venv .venv
.venv\Scripts\activate

 3. Install dependencies:

pip install -r requirements.txt

4. Running the project

streamlit run app.py


The app will open in a web browser, where images can be uploaded and analyzed interactively.

## Running tests

Basic unit tests are provided for the data analysis and PFU/mL calculation logic.

To run tests:

python -m unittest

## Notes

This project was developed as part of a final assignment for a Python programming course.
The repository may evolve during implementation as features are added and improved.
