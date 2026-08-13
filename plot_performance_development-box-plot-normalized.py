#
# This script plots normalized performance development over time using box plot and saves them in two sizes.
#
# To run script python3.6 plot_performance_development-box-plot-normalized.py <rmax_statistics.csv>
#

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.patches import Patch

# Plot rmax stats as boxplot
def plot_rmax_statistics_boxplot(csv_file, output_file="rmax_trends_boxplot.png",
                                  figsize=(16, 8), label_fontsize=12, tick_fontsize=10,
                                  legend_fontsize=14, legend_loc='lower left', legend_ncol=1,
                                  legend_markerscale=1.0, legend_handlelength=2.0,
                                  legend_labelspacing=0.5, legend_borderpad=0.4):

    # Load data
    df = pd.read_csv(csv_file)

    # Extract years
    years = []
    for list_name in df['List']:
        list_str = str(list_name)
        # Try to find year pattern
        year_match = re.search(r'(19|20)\d{2}', list_str)
        if year_match:
            years.append(int(year_match.group()))
        else:
            # Fallback: try first 4 digits
            year_str = ''.join(filter(str.isdigit, list_str))[:4]
            if len(year_str) == 4:
                years.append(int(year_str))
            else:
                years.append(None)

    df['Year'] = years

    # Normalize values - divide by Best (max)
    df['Best_Normalized'] = 1.0  # Best is always 1.0
    df['Worst_Normalized'] = df['Worst'] / df['Best']
    df['Q25_Normalized'] = df['Q25'] / df['Best']
    df['Median_Normalized'] = df['Median'] / df['Best']
    df['Q75_Normalized'] = df['Q75'] / df['Best']

    # Prepare data
    bp_data = []
    position_counter = 0
    x_tick_positions = []
    x_tick_labels = []

    years_seen = set()

    for idx, row in df.iterrows():
        # Create box plot from normalized quantiles
        box = {
            'whislo': row['Worst_Normalized'],  # Min (normalized)
            'q1': row['Q25_Normalized'],         # Q25 (normalized)
            'med': row['Median_Normalized'],     # Median (normalized)
            'q3': row['Q75_Normalized'],         # Q75 (normalized)
            'whishi': row['Best_Normalized'],    # Max (always 1.0)
            'fliers': []
        }
        bp_data.append(box)

        # Add x-axis label for every few years
        year = row['Year']
        if year is not None and year not in years_seen and year % 2 == 1:  # Show odd years
            x_tick_positions.append(position_counter)
            x_tick_labels.append(str(year))
            years_seen.add(year)

        position_counter += 1

    positions_list = list(range(len(bp_data)))

    # Colors
    box_color = '#56B4E9'      # Sky blue
    box_edge_color = '#0173B2'  # Dark blue
    median_color = '#009E73'   # Bluish green

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    ax.bxp(bp_data, positions=positions_list, widths=0.6,
           patch_artist=True, showfliers=False,
           boxprops=dict(facecolor=box_color, alpha=0.7, edgecolor=box_edge_color),
           medianprops=dict(color=median_color, linewidth=2.5),
           whiskerprops=dict(color=box_edge_color, linewidth=1.5),
           capprops=dict(color=box_edge_color, linewidth=1.5))

    # Set up x-axis with years
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=45, fontsize=tick_fontsize)
    ax.tick_params(axis='y', labelsize=tick_fontsize)

    # Labels
    ax.set_xlabel('TOP500 List Year', fontsize=label_fontsize, fontweight='bold')
    ax.set_ylabel('Normalized Rmax', fontsize=label_fontsize, fontweight='bold')

    # Set y-axis to logarithmic scale
    ax.set_yscale('log')

    # Add grid
    ax.grid(True, alpha=0.3, which='both', linestyle='--')

    # Add legend
    legend_elements = [
        Patch(facecolor=box_color, edgecolor=box_edge_color, alpha=0.7, label='Distribution (Q25-Q75)'),
        plt.Line2D([0], [0], color=median_color, linewidth=2.5, label='Median')
    ]
    ax.legend(handles=legend_elements, loc=legend_loc, fontsize=legend_fontsize, framealpha=1,
              ncol=legend_ncol, markerscale=legend_markerscale, handlelength=legend_handlelength,
              labelspacing=legend_labelspacing, borderpad=legend_borderpad)

    # Tight layout
    plt.tight_layout()

    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved as {output_file}")

    # Show plot
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot normalized Rmax performance development over time as a box plot, "
                    "saved as both a full-size PNG and a compact 5in PNG"
    )
    parser.add_argument("csv_file", help="Path to input rmax_statistics CSV file")
    parser.add_argument(
        "--full-output",
        default="rmax_trends_boxplot.png",
        help="Path to full-size output PNG file (default: rmax_trends_boxplot.png)"
    )
    parser.add_argument(
        "--compact-output",
        default="rmax_trends_boxplot_5in.png",
        help="Path to compact (5in-tall) output PNG file (default: rmax_trends_boxplot_5in.png)"
    )
    args = parser.parse_args()

    # Full-size
    plot_rmax_statistics_boxplot(args.csv_file, args.full_output, figsize=(16, 8))

    # 5in plot
    plot_rmax_statistics_boxplot(
        args.csv_file, args.compact_output, figsize=(16, 5),
        label_fontsize=14, tick_fontsize=13, legend_fontsize=13,
        legend_loc='lower left', legend_ncol=2, legend_markerscale=0.7,
        legend_handlelength=1.2, legend_labelspacing=0.25, legend_borderpad=0.3
    )
