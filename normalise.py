"""
normalise.py
------------
Handles loading the vowel CSV data and applying Lobanov (z-score) normalisation
to the F1/F2 formant values.

Lobanov normalisation converts each speaker's raw Hz values into z-scores:
    z = (x - mean) / std
This removes inter-speaker physiological differences, making vowel spaces
comparable across speakers. Within a single speaker, it centres and scales
the entire formant space to have mean=0 and std=1.
"""

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data(csv_path: str) -> pd.DataFrame:
    """
    Read the CSV file and return a cleaned DataFrame.

    Expected columns: Speaker, Vowel, F1, F2, context
    The 'context' column is dropped as it is not used in analysis or plotting.

    Parameters
    ----------
    csv_path : str
        Path to the input .csv file (tab-separated or comma-separated).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: Speaker, Vowel, F1, F2
    """
    # Try tab-separated first (as in the sample), fall back to comma-separated
    try:
        df = pd.read_csv(csv_path, sep='\t')
        # If only one column was parsed, it was probably comma-separated
        if df.shape[1] == 1:
            df = pd.read_csv(csv_path, sep=',')
    except Exception:
        df = pd.read_csv(csv_path)

    # Normalise column names: strip whitespace, lowercase
    df.columns = df.columns.str.strip().str.lower()

    # Drop the context column if it exists (not needed for analysis)
    if 'context' in df.columns:
        df = df.drop(columns=['context'])

    # Ensure the vowel column is a plain string and lowercased
    df['vowel'] = df['vowel'].astype(str).str.strip().str.lower()

    # Keep only the five target vowels
    valid_vowels = {'a', 'e', 'i', 'o', 'u'}
    df = df[df['vowel'].isin(valid_vowels)].copy()

    # Make sure F1 and F2 are numeric
    df['f1'] = pd.to_numeric(df['f1'], errors='coerce')
    df['f2'] = pd.to_numeric(df['f2'], errors='coerce')
    df = df.dropna(subset=['f1', 'f2'])

    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Lobanov normalisation
# ---------------------------------------------------------------------------

def lobanov_normalise(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply Lobanov (z-score) normalisation to F1 and F2.

    For each speaker the normalised values are calculated as:
        F1_N = (F1 - mean(F1_speaker)) / std(F1_speaker)
        F2_N = (F2 - mean(F2_speaker)) / std(F2_speaker)

    The means and standard deviations are computed across *all* tokens
    produced by that speaker (pooled across all vowel categories), which
    is the standard Lobanov (1971) procedure.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: speaker, vowel, f1, f2

    Returns
    -------
    pd.DataFrame
        Original DataFrame with two new columns added:
        'f1_norm' and 'f2_norm' (Lobanov-normalised values).
    """
    df = df.copy()
    df['f1_norm'] = np.nan
    df['f2_norm'] = np.nan

    for speaker_id, group in df.groupby('speaker'):
        # Compute per-speaker grand mean and std across ALL vowel tokens
        f1_mean = group['f1'].mean()
        f1_std  = group['f1'].std(ddof=1)   # sample std (Lobanov convention)
        f2_mean = group['f2'].mean()
        f2_std  = group['f2'].std(ddof=1)

        # Guard against zero std (should not happen with real data, but safe)
        if f1_std == 0:
            f1_std = 1.0
        if f2_std == 0:
            f2_std = 1.0

        idx = group.index
        df.loc[idx, 'f1_norm'] = (group['f1'] - f1_mean) / f1_std
        df.loc[idx, 'f2_norm'] = (group['f2'] - f2_mean) / f2_std

    return df


# ---------------------------------------------------------------------------
# Cluster midpoints
# ---------------------------------------------------------------------------

def compute_cluster_midpoints(df: pd.DataFrame) -> dict:
    """
    Compute the centroid (mean F1_norm, mean F2_norm) for each vowel cluster.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns 'vowel', 'f1_norm', 'f2_norm'.

    Returns
    -------
    dict
        {vowel: {'f1_mid': float, 'f2_mid': float}}
    """
    midpoints = {}
    for vowel, group in df.groupby('vowel'):
        midpoints[vowel] = {
            'f1_mid': group['f1_norm'].mean(),
            'f2_mid': group['f2_norm'].mean(),
        }
    return midpoints