"""
Vowel Space Plotter — Lobanov Normalisation
============================================
Input:  CSV with columns: Speaker, F1, F2, Vowel
Output: vowel_space.png  (and vowel_space.pdf)

Lobanov normalisation computes per-speaker z-scores:
    F*n = (Fn - mean_speaker(Fn)) / sd_speaker(Fn)

The vowel space is plotted with axes inverted (phonetic convention):
    x-axis: F2* (high → low, i.e. front → back)
    y-axis: F1* (low → high, i.e. open → close)
"""

import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path

# ── colour palette (one per vowel, colourblind-friendly) ──────────────────────
VOWEL_COLOURS = {
    "a":  "#E63946",
    "e":  "#F4A261",
    "i":  "#2A9D8F",
    "o":  "#457B9D",
    "u":  "#9B5DE5",
    "æ":  "#F77F00",
    "ɪ":  "#06D6A0",
    "ʊ":  "#118AB2",
    "ʌ":  "#EF476F",
    "ɔ":  "#073B4C",
    "ə":  "#8338EC",
}
DEFAULT_COLOUR = "#555555"

# ── marker cycle (one per speaker) ────────────────────────────────────────────
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*", "h", "8"]


# ─────────────────────────────────────────────────────────────────────────────
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    required = {"Speaker", "F1", "F2", "Vowel"}
    missing = required - set(df.columns)
    if missing:
        sys.exit(f"ERROR: CSV is missing columns: {missing}\n"
                 f"Found columns: {list(df.columns)}")

    df["F1"] = pd.to_numeric(df["F1"], errors="coerce")
    df["F2"] = pd.to_numeric(df["F2"], errors="coerce")
    n_bad = df[["F1", "F2"]].isna().any(axis=1).sum()
    if n_bad:
        warnings.warn(f"Dropping {n_bad} rows with non-numeric F1/F2.")
        df = df.dropna(subset=["F1", "F2"])

    return df


# ─────────────────────────────────────────────────────────────────────────────
def lobanov_normalise(df: pd.DataFrame) -> pd.DataFrame:
    """Add F1_lob and F2_lob columns (per-speaker z-scores)."""
    rows = []
    for speaker, grp in df.groupby("Speaker"):
        grp = grp.copy()
        for fn in ("F1", "F2"):
            mu = grp[fn].mean()
            sd = grp[fn].std(ddof=1)
            col = f"{fn}_lob"
            if sd == 0 or np.isnan(sd):
                warnings.warn(f"Speaker {speaker}: SD of {fn} is 0 or NaN; "
                              "z-scores set to 0.")
                grp[col] = 0.0
            else:
                grp[col] = (grp[fn] - mu) / sd
        rows.append(grp)
    return pd.concat(rows, ignore_index=True)


# ─────────────────────────────────────────────────────────────────────────────
def compute_ellipse(x, y, n_std=1.5):
    """Return (cx, cy, width, height, angle) for a covariance ellipse."""
    if len(x) < 3:
        return None
    cov = np.cov(x, y)
    vals, vecs = np.linalg.eigh(cov)
    # largest eigenvector gives the angle
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    angle = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
    width, height = 2 * n_std * np.sqrt(np.abs(vals))
    return np.mean(x), np.mean(y), width, height, angle


# ─────────────────────────────────────────────────────────────────────────────
def plot_vowel_space(df_norm: pd.DataFrame, out_stem: str = "vowel_space"):
    speakers = sorted(df_norm["Speaker"].unique())
    vowels   = sorted(df_norm["Vowel"].unique())
    n_speakers = len(speakers)

    fig, ax = plt.subplots(figsize=(8, 7))
    fig.patch.set_facecolor("#FAFAF8")
    ax.set_facecolor("#FAFAF8")

    for sp_idx, speaker in enumerate(speakers):
        sp_df  = df_norm[df_norm["Speaker"] == speaker]
        marker = MARKERS[sp_idx % len(MARKERS)]

        for vowel in vowels:
            colour = VOWEL_COLOURS.get(vowel, DEFAULT_COLOUR)
            vdf    = sp_df[sp_df["Vowel"] == vowel]
            x      = vdf["F2_lob"].values   # F2 → x-axis
            y      = vdf["F1_lob"].values   # F1 → y-axis

            # scatter — individual tokens
            ax.scatter(x, y,
                       color=colour, marker=marker,
                       s=55, alpha=0.55, linewidths=0.4,
                       edgecolors="white", zorder=3)

            # confidence ellipse (≥3 tokens) or reference circle (1-2 tokens)
            ell_params = compute_ellipse(x, y)
            if ell_params:
                cx, cy, w, h, angle = ell_params
                ell = mpatches.Ellipse(
                    (cx, cy), width=w, height=h, angle=angle,
                    linewidth=1.4, edgecolor=colour,
                    facecolor=colour, alpha=0.12, zorder=2
                )
                ax.add_patch(ell)
            elif len(x) > 0:
                # too few points for a covariance ellipse — draw a fixed-radius
                # reference circle so the speaker still has a visible marker.
                # The dashed border distinguishes it from a data-driven ellipse.
                cx, cy = np.mean(x), np.mean(y)
                circle = mpatches.Circle(
                    (cx, cy), radius=0.18,
                    linewidth=1.2, linestyle="--",
                    edgecolor=colour, facecolor=colour,
                    alpha=0.15, zorder=2
                )
                ax.add_patch(circle)

            # centroid label
            if len(x):
                ax.text(np.mean(x), np.mean(y), vowel,
                        ha="center", va="center",
                        fontsize=13, fontweight="bold",
                        color=colour,
                        fontfamily="DejaVu Sans",
                        zorder=4)

    # ── axes: invert both (phonetic convention) ───────────────────────────────
    ax.invert_xaxis()
    ax.invert_yaxis()

    ax.set_xlabel("F2* (Lobanov z-score)", fontsize=11, labelpad=8)
    ax.set_ylabel("F1* (Lobanov z-score)", fontsize=11, labelpad=8)
    ax.set_title("Vowel Space — Lobanov Normalisation",
                 fontsize=14, fontweight="bold", pad=14)

    ax.tick_params(labelsize=9)
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5, color="#CCCCCC")
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color("#AAAAAA")

    # ── legend: vowels (colour) + speakers (marker) ───────────────────────────
    vowel_handles = [
        Line2D([0], [0], marker="o", color="w",
               markerfacecolor=VOWEL_COLOURS.get(v, DEFAULT_COLOUR),
               markersize=9, label=f"/{v}/")
        for v in vowels
    ]
    speaker_handles = [
        Line2D([0], [0], marker=MARKERS[i % len(MARKERS)], color="w",
               markerfacecolor="#555555", markersize=8,
               label=f"Speaker {sp}")
        for i, sp in enumerate(speakers)
    ] if n_speakers > 1 else []

    handles = vowel_handles + speaker_handles
    titles  = (["Vowels"] + [""] * (len(vowel_handles) - 1) +
               (["Speakers"] + [""] * (len(speaker_handles) - 1)
                if speaker_handles else []))

    leg = ax.legend(handles=handles,
                    labels=[h.get_label() for h in handles],
                    loc="upper right", fontsize=9,
                    framealpha=0.85, edgecolor="#CCCCCC",
                    title="Legend", title_fontsize=9)
    leg.get_frame().set_linewidth(0.8)

    # ── annotation ────────────────────────────────────────────────────────────
    ax.annotate("front ←  F2  → back", xy=(0.5, -0.07),
                xycoords="axes fraction", ha="center",
                fontsize=8, color="#888888", style="italic")
    ax.annotate("open\n↕\nclose", xy=(-0.1, 0.5),
                xycoords="axes fraction", ha="center", va="center",
                fontsize=8, color="#888888", style="italic",
                rotation=90)
    ax.annotate("dashed circle = reference point\n(too few tokens for ellipse)",
                xy=(0.02, 0.02), xycoords="axes fraction",
                fontsize=7, color="#999999", style="italic",
                va="bottom")

    plt.tight_layout()

    png_path = f"{out_stem}.png"
    pdf_path = f"{out_stem}.pdf"
    fig.savefig(png_path, dpi=180, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    print(f"Saved: {png_path}")
    print(f"Saved: {pdf_path}")
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
def main():
    # ── resolve input path ────────────────────────────────────────────────────
    if len(sys.argv) >= 2:
        csv_path = sys.argv[1]
    else:
        # default: look for any .csv in the current directory
        csvs = list(Path(".").glob("*.csv"))
        if not csvs:
            sys.exit("Usage: python vowel_space.py <your_data.csv>\n"
                     "No .csv file found in the current directory.")
        csv_path = str(csvs[0])
        print(f"No file specified — using: {csv_path}")

    out_stem = Path(csv_path).stem + "_vowelspace"

    df      = load_data(csv_path)
    df_norm = lobanov_normalise(df)

    print(f"\nLoaded {len(df)} tokens | "
          f"{df['Speaker'].nunique()} speaker(s) | "
          f"{df['Vowel'].nunique()} vowel(s): {sorted(df['Vowel'].unique())}\n")

    # print per-vowel centroid summary
    summary = (df_norm.groupby("Vowel")[["F1_lob", "F2_lob"]]
               .agg(["mean", "std"])
               .round(3))
    print("Per-vowel centroids (Lobanov z-scores):")
    print(summary.to_string())
    print()

    plot_vowel_space(df_norm, out_stem=out_stem)


if __name__ == "__main__":
    main()