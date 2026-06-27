#
# This script plots performance development over time.
# It overlays best (First), worst (Last) and Sum of Rmax for two datasets so
# they can be compared on the same graph:
#   - Academic     systems (from rmax_statistics.csv)              -> solid lines
#   - Non-academic systems (from rmax_statistics_non_academic.csv) -> dashed lines
#
# To run script 'python3.6 plot_performance_development.py'
#


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re


def extract_years(df):
    """Extract a 4-digit year from each entry in the List column."""
    years = []
    for list_name in df['List']:
        list_str = str(list_name)
        year_match = re.search(r'(19|20)\d{2}', list_str)
        if year_match:
            years.append(int(year_match.group()))
        else:
            year_str = ''.join(filter(str.isdigit, list_str))[:4]
            years.append(int(year_str) if len(year_str) == 4 else None)
    return years


def plot_rmax_statistics(academic_file="rmax_statistics.csv",
                         non_academic_file="rmax_statistics_non_academic.csv",
                         output_file="rmax_trends.png"):

    # Load both datasets
    acad = pd.read_csv(academic_file)
    non_acad = pd.read_csv(non_academic_file)

    # Years (used for x-axis labels) come from the academic file
    years = extract_years(acad)

    # x-axis positions
    x_acad = np.arange(len(acad))
    x_non = np.arange(len(non_acad))

    # Create figure with logarithmic y-axis
    fig, ax = plt.subplots(figsize=(14, 8))

    # Colorblind-friendly palette (Okabe-Ito)
    # Non-Academic colors
    first_color_na = '#009E73'    # Bluish green
    last_color_na = '#0173B2'     # Blue
    sum_color_na = '#D55E00'      # Vermillion/red-orange
    # Academic colors
    first_color = '#90EE90' # light green
    last_color = '#56B4E9'  # Sky blue
    sum_color = '#E69F00'   # Amber/orange

    # Non-Academic - solid lines
    ax.plot(x_non, non_acad['Best'].values, marker='o', linewidth=2, markersize=6,
            label='First (Non-Academic)', color=first_color_na, alpha=0.85)
    ax.plot(x_non, non_acad['Worst'].values, marker='s', linewidth=2, markersize=6,
            label='Last (Non-Academic)', color=last_color_na, alpha=0.85)
    ax.plot(x_non, non_acad['Sum'].values, marker='^', linewidth=2, markersize=6,
            label='Sum (Non-Academic)', color=sum_color_na, alpha=0.85)

    # Academic - dashed lines, distinct colors per metric
    ax.plot(x_acad, acad['Best'].values, marker='o', linewidth=2, markersize=6,
            label='First (Academic)', color=first_color, alpha=0.85, linestyle='--')
    ax.plot(x_acad, acad['Worst'].values, marker='s', linewidth=2, markersize=6,
            label='Last (Academic)', color=last_color, alpha=0.85, linestyle='--')
    ax.plot(x_acad, acad['Sum'].values, marker='^', linewidth=2, markersize=6,
            label='Sum (Academic)', color=sum_color, alpha=0.85, linestyle='--')

    # Set logarithmic scale for y-axis
    ax.set_yscale('log')

    # Set up x-axis with years
    unique_years = sorted(set([y for y in years if y is not None]))
    step = max(1, len(unique_years) // 15)
    selected_years = unique_years[::step]

    year_positions = []
    for year in selected_years:
        idx = next((i for i, y in enumerate(years) if y == year), None)
        if idx is not None:
            year_positions.append(idx)

    ax.set_xticks(year_positions)
    ax.set_xticklabels(selected_years, rotation=45)

    # Labels
    ax.set_xlabel('TOP500 List Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Rmax (TFlop/s)', fontsize=12, fontweight='bold')

    # Grid
    ax.grid(True, alpha=0.3, which='both', linestyle='--')

    # Legend
    ax.legend(loc='upper left', fontsize=12, framealpha=1, ncol=2)

    # Tight layout
    plt.tight_layout()

    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved as {output_file}")

    # Show plot
    plt.show()


if __name__ == "__main__":
    plot_rmax_statistics()
