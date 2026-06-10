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
python3 script.py <csv_file>
```

**Arguments:**

- `csv_file` — path to your input `.csv` file (see format below)

**Example:**

```bash
python3 script.py my_data.csv
```

This will create:
- A `results/{group}/` subdirectory for each group in the data
- `results/{speaker}.png` — vowel space plot
- `results/{speaker}_clustermidpoints.txt` — cluster midpoint coordinates
For each speaker in each group. It will also create:
- `results/{speaker}.png`

The `results/` folder and all subdirectories are created automatically if they does not exist.

---

## Input Format

The CSV should be comma-separated with the following columns:

|Group| | Speaker | Vowel | F1 | F2 | Notes |
|test | | #1      | a     | X  | Y  | ...   |

- **Group** - group name/ID
- **Speaker** — speaker ID
- **Vowel** — one of `a`, `e`, `i`, `o`, `u`. Note that as I made the application to analyse Spanish vowels, I only made it with these vowels in mind. More could be added later when I have more time.
- **F1 / F2** — formant values in Hz
- **Notes** — ignored by the tool, optional inclusion

---

## Output

**Plot (`.png`)** — the Lobanov-normalised vowel space showing:
- Individual token scatter points per vowel
- A covariance ellipse (2 SD) around each vowel cluster
- Centroid marker and label for each vowel
- Axes oriented to phonetic convention (F2 right→left, F1 bottom→top)

**Midpoints (`.txt`)** — the F1 and F2 normalised centroid coordinates for each vowel cluster, also printed to the terminal on each run.

- These will be outputted for each individual speaker, and an aggregate plot and midpoints will be outputted for each group.
- A preview of the output given the current data.csv file can be viewed in the ```results/``` folder
---

## Acknowledgements

**Libraries:** [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [Matplotlib](https://matplotlib.org/)

**Normalisation method:** Lobanov, B. M. (1971). Classification of Russian vowels spoken by different speakers. *Journal of the Acoustical Society of America*, 49(2B), 606–608.

**AI assistance:** This project was developed with the assistance of [Claude](https://claude.ai) (Anthropic), which was used to generate the initial Python code across all modules. Later edits to the code were made by the user to improve presentation of data and project layout. Claude was used as a coding tool to assist in the automation of the data visualisation process, the analysis approach and data itself was provided by the user.