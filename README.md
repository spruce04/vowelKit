# Vowel Kit

A Python tool for Lobanov (z-score) normalisation of vowel formant data (F1/F2), with visualisation of the normalised vowel space and cluster midpoint output.

---

## Requirements

- Python 3.8+
- `pandas`
- `numpy`
- `matplotlib`

Install dependencies with:

```bash
pip install pandas numpy matplotlib
```

---

## Usage
Navigate to the src folder (```cd ./src```), and enter:
```bash
python3 script.py <csv_file> <output_name>
```

**Arguments:**

- `csv_file` — path to your input `.csv` file (see format below)
- `output_name` — base name for output files (no extension needed)

**Example:**

```bash
python3 script.py my_data.csv speaker1
```

This will create:
- `results/speaker1.png` — vowel space plot
- `results/speaker1_clustermidpoints.txt` — cluster midpoint coordinates

The `results/` folder is created automatically if it does not exist.

---

## Input Format

The CSV should be tab-separated with the following columns:

| Speaker | Vowel | F1 | F2 | context |
|---|---|---|---|---|
| 1 | a | 715.15 | 1523.96 | … |

- **Speaker** — speaker ID (currently supports single-speaker files)
- **Vowel** — one of `a`, `e`, `i`, `o`, `u`
- **F1 / F2** — formant values in Hz
- **context** — ignored by the tool, optional inclusion

---

## Output

**Plot (`.png`)** — the Lobanov-normalised vowel space showing:
- Individual token scatter points per vowel
- A covariance ellipse (2 SD) around each vowel cluster
- Centroid marker and label for each vowel
- Axes oriented to phonetic convention (F2 right→left, F1 bottom→top)

**Midpoints (`.txt`)** — the F1 and F2 normalised centroid coordinates for each vowel cluster, also printed to the terminal on each run.

---

## Acknowledgements

**Libraries:** [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [Matplotlib](https://matplotlib.org/)

**Normalisation method:** Lobanov, B. M. (1971). Classification of Russian vowels spoken by different speakers. *Journal of the Acoustical Society of America*, 49(2B), 606–608.

**AI assistance:** This project was developed with the assistance of [Claude](https://claude.ai) (Anthropic), which was used to generate the initial Python code across all modules. Later edits to the code were made by the user to improve presentation of data and project layout. Claude was used as a coding tool to assist in the automation of the data visualisation process, the analysis approach and data itself was provided by the user.