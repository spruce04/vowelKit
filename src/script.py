"""
script.py
---------
Entry point for the vowel normalisation and plotting pipeline.

Usage
-----
    python3 script.py <csv_file>

Arguments
---------
    csv_file      Path to the input CSV file containing vowel formant data.

Output structure
----------------
    results/
        {group}/
            {speaker}.png
            {speaker}_clustermidpoints.txt
            ...
            {group}_aggregate.png
            {group}_aggregate_clustermidpoints.txt
        ...

Pipeline overview
-----------------
    1.  Load and clean the CSV                          (normalise.py)
    2.  For each Group:
        a.  For each Speaker in the group:
              i.  Apply Lobanov normalisation            (normalise.py)
             ii.  Compute cluster midpoints             (normalise.py)
            iii.  Print midpoints to terminal           (output_results.py)
             iv.  Save midpoints .txt                   (output_results.py)
              v.  Plot vowel space, save PNG            (plot_vowels.py)
        b.  Pool all normalised speaker data for group
        c.  Compute aggregate midpoints                 (normalise.py)
        d.  Save aggregate midpoints .txt               (output_results.py)
        e.  Plot aggregate vowel space, save PNG        (plot_vowels.py)
"""

import sys
import os
import pandas as pd

from normalise import load_data, lobanov_normalise, compute_cluster_midpoints
from plot_vowels import plot_vowel_space
from output_results import save_midpoints_txt


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    """
    Parse and validate command-line arguments.

    Returns
    -------
    csv_path : str — path to the input CSV file
    """
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <csv_file>")
        print("Example: python3 script.py data.csv")
        sys.exit(1)

    csv_path = sys.argv[1]

    if not os.path.isfile(csv_path):
        print(f"Error: CSV file not found: '{csv_path}'")
        sys.exit(1)

    return csv_path


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    # ── Step 0: Parse arguments ─────────────────────────────────────────────
    csv_path = parse_args()

    # ── Step 1: Load data ───────────────────────────────────────────────────
    print(f"\n[data]   Loading  →  {csv_path}")
    df = load_data(csv_path)
    print(f"[data]   {len(df)} tokens loaded  |  vowels: {sorted(df['vowel'].unique())}")

    if 'group' not in df.columns:
        print("[error]  'Group' column not found. Please check the required "
              "formatting in the README.")
        sys.exit(1)

    if 'speaker' not in df.columns:
        print("[error]  'Speaker' column not found. Please check the required "
              "formatting in the README.")
        sys.exit(1)

    results_dir = '../results'

    # ── Step 2: Process each group ──────────────────────────────────────────
    for group_id, group_df in df.groupby('group'):

        print(f"\n{'━'*54}")
        print(f"[group]  Processing group: {group_id}")
        print(f"{'━'*54}")

        # Output folder for this group
        group_dir = os.path.join(results_dir, str(group_id))
        os.makedirs(group_dir, exist_ok=True)

        # Collect each speaker's normalised data for the aggregate
        normalised_slices = []

        # ── Step 2a: Process each speaker within the group ──────────────────
        for speaker_id, speaker_df in group_df.groupby('speaker'):

            print(f"\n[speaker] {speaker_id}  "
                  f"({len(speaker_df)} tokens)")

            # Lobanov normalisation (operates per-speaker internally,
            # but we pass only this speaker's slice for clarity)
            norm_df = lobanov_normalise(speaker_df)
            normalised_slices.append(norm_df)

            # Cluster midpoints
            midpoints = compute_cluster_midpoints(norm_df)

            # Build output paths  →  results/{group}/{speaker}.*
            base = os.path.join(group_dir, str(speaker_id))
            save_midpoints_txt(
                midpoints,
                f"{base}_clustermidpoints.txt",
                speaker_label=speaker_id,
            )
            plot_vowel_space(
                norm_df,
                midpoints,
                f"{base}.png",
                speaker_label=speaker_id,
                group_label=group_id,
            )

        # ── Step 2b: Aggregate plot for the whole group ──────────────────────
        print(f"\n[group]  Building aggregate for group {group_id} …")

        agg_df = pd.concat(normalised_slices, ignore_index=True)
        agg_midpoints = compute_cluster_midpoints(agg_df)

        agg_base = os.path.join(group_dir, f"{group_id}_aggregate")
        save_midpoints_txt(
            agg_midpoints,
            f"{agg_base}_clustermidpoints.txt",
            speaker_label=f"Group {group_id} — aggregate",
        )
        plot_vowel_space(
            agg_df,
            agg_midpoints,
            f"{agg_base}.png",
            group_label=group_id,
            aggregate=True,
        )

    print(f"\n[done]   All outputs written to '{results_dir}/'")


if __name__ == '__main__':
    main()