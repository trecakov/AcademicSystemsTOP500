#
# This script plots performance development over time with top, last and sum of all Rmax for both academic and non-academic systems.
# The plot is saved as two sized PNG files.
#
# To run script python3.6 plot_performance_development_comparison.py rmax_statistics.csv rmax_statistics_non_academic.csv
#

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# Single-column
COLUMN_FIGSIZE = (3.5, 2.8)
COLUMN_LABEL_FONTSIZE = 9
COLUMN_TICK_FONTSIZE = 8
COLUMN_LEGEND_FONTSIZE = 8
COLUMN_LINEWIDTH = 1.2
COLUMN_MARKERSIZE = 3
COLUMN_MAX_TICKS = 6

# Full-size
FULL_FIGSIZE = (14, 8)
FULL_LABEL_FONTSIZE = 12
FULL_TICK_FONTSIZE = 10
FULL_LEGEND_FONTSIZE = 12
FULL_LINEWIDTH = 2
FULL_MARKERSIZE = 6
FULL_MAX_TICKS = 15

# Extract years
def extract_years(df):
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

# Plot rmax stats
def plot_rmax_statistics(academic_file, non_academic_file, output_file,
                          figsize, label_fontsize, tick_fontsize, legend_fontsize,
                          linewidth, markersize, max_ticks,
                          legend_loc='upper left', legend_ncol=2,
                          legend_markerscale=1.0, legend_handlelength=2.0,
                          legend_labelspacing=0.5, legend_borderpad=0.4):

    # Load datasets
    acad = pd.read_csv(academic_file)
    non_acad = pd.read_csv(non_academic_file)

    # x-axis labels
    years = extract_years(acad)

    # x-axis positions
    x_acad = np.arange(len(acad))
    x_non = np.arange(len(non_acad))

    # Figure and logarithmic y-axis
    fig, ax = plt.subplots(figsize=figsize)

    # Non-Academic colors
    first_color_na = '#009E73'    # Bluish green
    last_color_na = '#0173B2'     # Blue
    sum_color_na = '#D55E00'      # Vermillion/red-orange
    # Academic colors
    first_color = '#90EE90'  # light green
    last_color = '#56B4E9'   # Sky blue
    sum_color = '#E69F00'    # Amber/orange

    # Non-Academic - solid lines
    ax.plot(x_non, non_acad['Best'].values, marker='o', linewidth=linewidth, markersize=markersize,
            label='First (Non-Academic)', color=first_color_na, alpha=0.85)
    ax.plot(x_non, non_acad['Worst'].values, marker='s', linewidth=linewidth, markersize=markersize,
            label='Last (Non-Academic)', color=last_color_na, alpha=0.85)
    ax.plot(x_non, non_acad['Sum'].values, marker='^', linewidth=linewidth, markersize=markersize,
            label='Sum (Non-Academic)', color=sum_color_na, alpha=0.85)

    # Academic - dashed lines
    ax.plot(x_acad, acad['Best'].values, marker='o', linewidth=linewidth, markersize=markersize,
            label='First (Academic)', color=first_color, alpha=0.85, linestyle='--')
    ax.plot(x_acad, acad['Worst'].values, marker='s', linewidth=linewidth, markersize=markersize,
            label='Last (Academic)', color=last_color, alpha=0.85, linestyle='--')
    ax.plot(x_acad, acad['Sum'].values, marker='^', linewidth=linewidth, markersize=markersize,
            label='Sum (Academic)', color=sum_color, alpha=0.85, linestyle='--')

    # Logarithmic scale y-axis
    ax.set_yscale('log')

    # Set up x-axis
    unique_years = sorted(set([y for y in years if y is not None]))
    step = max(1, len(unique_years) // max_ticks)
    selected_years = unique_years[::step]

    year_positions = []
    for year in selected_years:
        idx = next((i for i, y in enumerate(years) if y == year), None)
        if idx is not None:
            year_positions.append(idx)

    ax.set_xticks(year_positions)
    ax.set_xticklabels(selected_years, rotation=45, fontsize=tick_fontsize)
    ax.tick_params(axis='y', labelsize=tick_fontsize)

    # Labels
    ax.set_xlabel('TOP500 List Year', fontsize=label_fontsize, fontweight='bold')
    ax.set_ylabel('Rmax (TFlop/s)', fontsize=label_fontsize, fontweight='bold')

    # Grid
    ax.grid(True, alpha=0.3, which='both', linestyle='--')

    # Legend
    ax.legend(
        loc=legend_loc, fontsize=legend_fontsize, framealpha=1, ncol=legend_ncol,
        markerscale=legend_markerscale, handlelength=legend_handlelength,
        labelspacing=legend_labelspacing, borderpad=legend_borderpad
    )

    # Tight layout
    plt.tight_layout()

    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved as {output_file}")

    # Show plot
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot Rmax performance development (First/Last/Sum) comparing academic "
                    "vs non-academic systems, saved both as a full-size PNG and a single-column PNG"
    )
    parser.add_argument("academic_file", help="Path to academic rmax_statistics CSV file")
    parser.add_argument("non_academic_file", help="Path to non-academic rmax_statistics CSV file")
    parser.add_argument(
        "--full-output",
        default="rmax_trends_full.png",
        help="Output filename for the full-size plot (default: rmax_trends_full.png)"
    )
    parser.add_argument(
        "--column-output",
        default="rmax_trends_column.png",
        help="Output filename for the single-column plot (default: rmax_trends_column.png)"
    )
    args = parser.parse_args()

    # Full-size
    plot_rmax_statistics(
        args.academic_file, args.non_academic_file, args.full_output,
        figsize=FULL_FIGSIZE, label_fontsize=FULL_LABEL_FONTSIZE,
        tick_fontsize=FULL_TICK_FONTSIZE, legend_fontsize=FULL_LEGEND_FONTSIZE,
        linewidth=FULL_LINEWIDTH, markersize=FULL_MARKERSIZE, max_ticks=FULL_MAX_TICKS,
        legend_loc='upper left', legend_ncol=2
    )

    # Single-column 
    plot_rmax_statistics(
        args.academic_file, args.non_academic_file, args.column_output,
        figsize=COLUMN_FIGSIZE, label_fontsize=COLUMN_LABEL_FONTSIZE,
        tick_fontsize=COLUMN_TICK_FONTSIZE, legend_fontsize=6,
        linewidth=COLUMN_LINEWIDTH, markersize=COLUMN_MARKERSIZE, max_ticks=COLUMN_MAX_TICKS,
        legend_loc='upper left', legend_ncol=1,
        legend_markerscale=0.9, legend_handlelength=1.4,
        legend_labelspacing=0.3, legend_borderpad=0.35
    )
