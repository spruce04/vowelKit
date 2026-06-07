"""
script.py
---------
Entry point for the vowel normalisation and plotting pipeline.

Usage
-----
    python3 script.py <csv_file> <output_name>

Arguments
---------
    csv_file      Path to the input CSV file containing vowel formant data.
    output_name   Base name (no extension) for output files.
                  The plot will be saved as:
                      results/<output_name>.png
                  The midpoints text will be saved as:
                      results/<output_name>_clustermidpoints.txt

Example
-------
    python3 script.py data.csv speaker1
    # → results/speaker1.png
    # → results/speaker1_clustermidpoints.txt

Pipeline overview
-----------------
    1. Load and clean the CSV                     (normalise.py)
    2. Apply Lobanov (z-score) normalisation       (normalise.py)
    3. Compute cluster midpoints                   (normalise.py)
    4. Print midpoints to the terminal             (output_results.py)
    5. Save midpoints to a .txt file               (output_results.py)
    6. Plot the vowel space and save as PNG        (plot_vowels.py)
"""

import sys
import os

# ── Import project modules ──────────────────────────────────────────────────
from normalise import load_data, lobanov_normalise, compute_cluster_midpoints
from plot_vowels import plot_vowel_space
from output_results import print_midpoints, save_midpoints_txt


# ---------------------------------------------------------------------------
# Argument parsing (manual, no external dependencies)
# ---------------------------------------------------------------------------

def parse_args():
    """
    Parse and validate command-line arguments.

    Returns
    -------
    csv_path    : str  — path to the input CSV file
    output_name : str  — base name for output files (no extension)
    """
    if len(sys.argv) != 3:
        print("Usage: python3 script.py <csv_file> <output_name>")
        print("Example: python3 script.py data.csv speaker1")
        sys.exit(1)

    csv_path = sys.argv[1]
    output_name = sys.argv[2]

    if not os.path.isfile(csv_path):
        print(f"Error: CSV file not found: '{csv_path}'")
        sys.exit(1)

    return csv_path, output_name


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    # ── Step 0: Parse arguments ─────────────────────────────────────────────
    csv_path, output_name = parse_args()

    # ── Step 1: Build output paths ──────────────────────────────────────────
    results_dir = '../results'
    os.makedirs(results_dir, exist_ok=True)

    plot_path       = os.path.join(results_dir, f"{output_name}.png")
    midpoints_path  = os.path.join(results_dir, f"{output_name}_clustermidpoints.txt")

    # ── Step 2: Load data ───────────────────────────────────────────────────
    print(f"\n[data]   Loading  →  {csv_path}")
    df = load_data(csv_path)
    print(f"[data]   {len(df)} tokens loaded  |  vowels: {sorted(df['vowel'].unique())}")

    # Identify the speaker (assumed to be a single speaker)
    speaker_id = df['speaker'].iloc[0] if 'speaker' in df.columns else None

    # ── Step 3: Lobanov normalisation ───────────────────────────────────────
    print("[norm]   Applying Lobanov (z-score) normalisation …")
    df = lobanov_normalise(df)

    # ── Step 4: Compute cluster midpoints ───────────────────────────────────
    midpoints = compute_cluster_midpoints(df)

    # ── Step 5: Print midpoints to terminal ─────────────────────────────────
    print_midpoints(midpoints, speaker_label=speaker_id)

    # ── Step 6: Save midpoints to .txt ──────────────────────────────────────
    save_midpoints_txt(midpoints, midpoints_path, speaker_label=speaker_id)

    # ── Step 7: Plot vowel space and save PNG ───────────────────────────────
    plot_vowel_space(df, midpoints, plot_path, speaker_label=speaker_id)

    print(f"\n[done]   All outputs written to '{results_dir}/'")


if __name__ == '__main__':
    main()