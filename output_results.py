"""
output_results.py
-----------------
Handles writing the cluster midpoint data to:
  1. The terminal (stdout)
  2. A plaintext .txt file

Kept separate from normalise.py and plot_vowels.py so that each file
has a single clear responsibility.
"""

import os


# Consistent ordering for the five vowels
VOWEL_ORDER = ['a', 'e', 'i', 'o', 'u']


# ---------------------------------------------------------------------------
# Terminal output
# ---------------------------------------------------------------------------

def print_midpoints(midpoints: dict, speaker_label=None):
    """
    Print a formatted summary of cluster midpoints to the terminal.

    Parameters
    ----------
    midpoints    : dict        — {vowel: {'f1_mid': float, 'f2_mid': float}}
    speaker_label : str|None  — optional speaker ID for the header
    """
    header = "═" * 46
    print("\n" + header)
    if speaker_label is not None:
        print(f"  Vowel Cluster Midpoints  —  Speaker {speaker_label}")
    else:
        print("  Vowel Cluster Midpoints (Lobanov normalised)")
    print(header)
    print(f"  {'Vowel':<10}  {'F1_norm (mid)':>15}  {'F2_norm (mid)':>15}")
    print("  " + "─" * 42)

    for vowel in VOWEL_ORDER:
        if vowel not in midpoints:
            continue
        f1 = midpoints[vowel]['f1_mid']
        f2 = midpoints[vowel]['f2_mid']
        print(f"  /{vowel}/ {'':<6}  {f1:>15.6f}  {f2:>15.6f}")

    print(header + "\n")


# ---------------------------------------------------------------------------
# File output
# ---------------------------------------------------------------------------

def save_midpoints_txt(midpoints: dict, output_path: str, speaker_label=None):
    """
    Write the cluster midpoints to a plain-text file.

    Parameters
    ----------
    midpoints    : dict  — {vowel: {'f1_mid': float, 'f2_mid': float}}
    output_path  : str   — destination file path (e.g. results/name_clustermidpoints.txt)
    speaker_label : str|None — optional speaker ID
    """
    # Make sure the output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

    lines = []
    lines.append("Vowel Cluster Midpoints — Lobanov Normalised")
    if speaker_label is not None:
        lines.append(f"Speaker: {speaker_label}")
    lines.append("")
    lines.append(f"{'Vowel':<10}  {'F1_norm_midpoint':>18}  {'F2_norm_midpoint':>18}")
    lines.append("─" * 50)

    for vowel in VOWEL_ORDER:
        if vowel not in midpoints:
            continue
        f1 = midpoints[vowel]['f1_mid']
        f2 = midpoints[vowel]['f2_mid']
        lines.append(f"/{vowel}/ {'':<6}  {f1:>18.6f}  {f2:>18.6f}")

    lines.append("")
    lines.append("Note: values are Lobanov (z-score) normalised.")
    lines.append("F1 low  → high vowel  |  F1 high  → low vowel")
    lines.append("F2 high → front vowel |  F2 low   → back vowel")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f"[output] Saved midpoints text  →  {output_path}")