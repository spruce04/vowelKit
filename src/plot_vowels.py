"""
plot_vowels.py
--------------
Handles all plotting logic: draws the normalised vowel space with
confidence ellipses around each vowel cluster and marks centroids.

The vowel space is plotted with:
  - F2_norm on the X-axis (reversed, so front vowels appear on the left,
    following the phonetic convention of high F2 = front)
  - F1_norm on the Y-axis (reversed, so high vowels appear at the top,
    following the phonetic convention of low F1 = high vowel)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')           # Non-interactive backend (safe for scripts)
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse


# ---------------------------------------------------------------------------
# Colour palette and vowel labels
# ---------------------------------------------------------------------------

# Distinct colours for each of the five vowels
VOWEL_COLOURS = {
    'a': '#E63946',   # vivid red
    'e': '#2A9D8F',   # teal
    'i': '#457B9D',   # steel blue
    'o': '#E9C46A',   # warm yellow
    'u': '#9B5DE5',   # purple
}

VOWEL_ORDER = ['a', 'e', 'i', 'o', 'u']


# ---------------------------------------------------------------------------
# Confidence ellipse helper
# ---------------------------------------------------------------------------

def _confidence_ellipse(x, y, ax, n_std=2.0, **kwargs):
    """
    Draw a covariance-based confidence ellipse on *ax* for data (x, y).

    The ellipse covers approximately the region within *n_std* standard
    deviations of the bivariate normal distribution fit to the data.

    Parameters
    ----------
    x, y   : array-like  — data coordinates
    ax     : Axes        — matplotlib axes to draw on
    n_std  : float       — number of std devs for ellipse radius (default 2)
    **kwargs             — passed to matplotlib.patches.Ellipse
    """
    if len(x) < 3:
        # Not enough points to estimate a covariance matrix reliably
        return

    cov = np.cov(x, y)
    # Eigendecomposition of the covariance matrix gives ellipse orientation
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    # Angle of the major axis in degrees
    angle = np.degrees(np.arctan2(*eigenvectors[:, 0][::-1]))
    # Width and height are proportional to sqrt of eigenvalues * n_std
    width  = 2 * n_std * np.sqrt(eigenvalues[0])
    height = 2 * n_std * np.sqrt(eigenvalues[1])

    ellipse = Ellipse(
        xy=(np.mean(x), np.mean(y)),
        width=width,
        height=height,
        angle=angle,
        **kwargs,
    )
    ax.add_patch(ellipse)


# ---------------------------------------------------------------------------
# Main plotting function
# ---------------------------------------------------------------------------

def plot_vowel_space(df, midpoints: dict, output_path: str, speaker_label=None):
    """
    Create and save the normalised vowel space plot.

    Each vowel category is drawn with:
      1. Scatter points (raw tokens)
      2. A filled confidence ellipse (2 SD, semi-transparent)
      3. A centroid marker with the vowel IPA label

    The axes follow standard phonetic orientation:
      - F2 increases right-to-left (front vowels on the left)
      - F1 increases bottom-to-top  (high vowels at the top)

    Parameters
    ----------
    df          : pd.DataFrame  — normalised data with 'vowel', 'f1_norm', 'f2_norm'
    midpoints   : dict          — {vowel: {'f1_mid': …, 'f2_mid': …}}
    output_path : str           — file path for the saved PNG
    speaker_label : str|int|None — optional speaker ID for the title
    """
    fig, ax = plt.subplots(figsize=(8, 7))
    fig.patch.set_facecolor('#FAFAFA')
    ax.set_facecolor('#F4F4F4')

    for vowel in VOWEL_ORDER:
        subset = df[df['vowel'] == vowel]
        if subset.empty:
            continue

        colour = VOWEL_COLOURS[vowel]
        x = subset['f2_norm'].values   # F2 on X-axis
        y = subset['f1_norm'].values   # F1 on Y-axis

        # ── 1. Confidence ellipse (filled, semi-transparent) ────────────────
        _confidence_ellipse(
            x, y, ax,
            n_std=2.0,
            facecolor=colour,
            alpha=0.18,
            edgecolor=colour,
            linewidth=2.0,
            linestyle='--',
            zorder=2,
        )

        # ── 2. Scatter: individual token points ─────────────────────────────
        ax.scatter(
            x, y,
            color=colour,
            s=40,
            alpha=0.65,
            edgecolors='white',
            linewidths=0.5,
            zorder=3,
        )

        # ── 3. Centroid marker ───────────────────────────────────────────────
        cx = midpoints[vowel]['f2_mid']
        cy = midpoints[vowel]['f1_mid']

        # Larger opaque point at centroid
        ax.scatter(
            cx, cy,
            color=colour,
            s=75,
            zorder=5,
            edgecolors='white',
            linewidths=1.5,
        )

        # Vowel label text next to the centroid
        ax.text(
            cx, cy,
            f' /{vowel}/',
            fontsize=15,
            fontweight='bold',
            color=colour,
            va='center',
            zorder=6,
        )

    # ── Axis formatting (reversed to match phonetic convention) ─────────────
    ax.invert_xaxis()   # F2: high values on left (front vowels left)
    ax.invert_yaxis()   # F1: high values at top  (high vowels top)

    ax.set_xlabel('F2 (Lobanov normalised)', fontsize=12, labelpad=8)
    ax.set_ylabel('F1 (Lobanov normalised)', fontsize=12, labelpad=8)

    title = 'Lobanov-Normalised Vowel Space'
    if speaker_label is not None:
        title += f'  —  Speaker {speaker_label}'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=14)

    ax.grid(True, linestyle=':', linewidth=0.7, color='#BBBBBB', alpha=0.8)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"[plot]  Saved vowel space plot  →  {output_path}")