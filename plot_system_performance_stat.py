#
# This script plots system performance statistics (Rmax/Rpeak) using box plot and produces a full-size plot and a compact 6in.
#
# To run script 'python3.6 plot_system_performance_stat.py system_performance_statistics.csv'
#

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

def plot_system_performance_boxplot(csv_file, output_file="system_performance_boxplot.png",
                                     figsize=(16, 8), label_fontsize=12, tick_fontsize=10,
                                     legend_fontsize=12, marker_size=80, legend_loc='upper left',
                                     legend_ncol=1, legend_markerscale=1.0, legend_handlelength=2.0,
                                     legend_labelspacing=0.5, legend_borderpad=0.4, year_step=1):

    # Load data
    df = pd.read_csv(csv_file)

    # Extract years
    years = []
    for date_code in df['Date']:
        date_str = str(date_code)
        if len(date_str) >= 4:
            year = int(date_str[:4])
            years.append(year)
        else:
            years.append(None)

    df['Year'] = years

    # Extract month
    months = []
    for date_code in df['Date']:
        date_str = str(date_code)
        if len(date_str) >= 6:
            month = int(date_str[4:6])
            months.append(month)
        else:
            months.append(None)

    df['Month'] = months

    # Group by year and month
    unique_year_months = sorted(set([(y, m) for y, m in zip(years, months) if y is not None and m is not None]))

    # Prepare data for box plots and top system line
    bp_data = []
    top_system_data = []
    position_counter = 0
    x_tick_positions = []
    x_tick_labels = []

    years_seen = set()

    for year, month in unique_year_months:
        year_month_data = df[(df['Year'] == year) & (df['Month'] == month)]

        for idx, row in year_month_data.iterrows():
            box = {
                'whislo': row['Worst'],
                'q1': row['Q25'],
                'med': row['Median'],
                'q3': row['Q75'],
                'whishi': row['Best'],
                'fliers': []
            }
            bp_data.append(box)
            top_system_data.append(row['Top_System_Performance'])

            if month == 6 and year not in years_seen:
                x_tick_positions.append(position_counter)
                x_tick_labels.append(str(year))
                years_seen.add(year)

            position_counter += 1

    positions_list = list(range(len(bp_data)))

    # x-ticks labels
    if year_step > 1:
        x_tick_positions = x_tick_positions[::year_step]
        x_tick_labels = x_tick_labels[::year_step]

    # Colors
    box_color = '#56B4E9'      # Sky blue
    box_edge_color = '#0173B2'  # Dark blue
    median_color = '#009E73'   # Bluish green
    top_system_color = '#D55E00'  # Vermillion/red-orange

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    ax.bxp(bp_data, positions=positions_list, widths=0.6,
           patch_artist=True, showfliers=False,
           boxprops=dict(facecolor=box_color, alpha=0.7, edgecolor=box_edge_color),
           medianprops=dict(color=median_color, linewidth=2.5),
           whiskerprops=dict(color=box_edge_color, linewidth=1.5),
           capprops=dict(color=box_edge_color, linewidth=1.5))

    # Overlay the #1 system performance as dots
    if any(y is not None for y in top_system_data):
        valid_positions = [p for p, y in zip(positions_list, top_system_data) if y is not None]
        valid_top_performance = [y for y in top_system_data if y is not None]

        ax.scatter(valid_positions, valid_top_performance, marker='o', s=marker_size,
                   color=top_system_color, alpha=0.9, zorder=6, edgecolors='black', linewidths=1)

    # Set up x-axis labels
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0, fontsize=tick_fontsize)
    ax.tick_params(axis='y', labelsize=tick_fontsize)

    # Labels
    ax.set_xlabel('TOP500 List Year', fontsize=label_fontsize, fontweight='bold')
    ax.set_ylabel('System Performance (Rmax/Rpeak)', fontsize=label_fontsize, fontweight='bold')

    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    # Add legend
    legend_elements = [
        Patch(facecolor=box_color, edgecolor=box_edge_color, alpha=0.7, label='Quantiles (Q25-Q75)'),
        plt.Line2D([0], [0], color=median_color, linewidth=2.5, label='Median'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=top_system_color,
               markersize=10, markeredgecolor='black', markeredgewidth=1, label='#1 System', linestyle='None')
    ]
    ax.legend(handles=legend_elements, loc=legend_loc, fontsize=legend_fontsize, framealpha=1,
              ncol=legend_ncol, markerscale=legend_markerscale, handlelength=legend_handlelength,
              labelspacing=legend_labelspacing, borderpad=legend_borderpad)

    # Set y-axis limits to show range from 0 to 1
    ax.set_ylim(0, 1.05)

    # Tight layout
    plt.tight_layout()

    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved as {output_file}")

    # Show plot
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot system performance (Rmax/Rpeak) statistics as a box plot, saved as "
                    "both a full-size PNG and a compact 6in PNG"
    )
    parser.add_argument("csv_file", help="Path to input system_performance_statistics CSV file")
    parser.add_argument(
        "--full-output",
        default="system_performance_boxplot.png",
        help="Path to full-size output PNG file (default: system_performance_boxplot.png)"
    )
    parser.add_argument(
        "--compact-output",
        default="system_performance_boxplot_6in.png",
        help="Path to compact 6in output PNG file (default: system_performance_boxplot_6in.png)"
    )
    args = parser.parse_args()

    # Full-size
    plot_system_performance_boxplot(args.csv_file, args.full_output, figsize=(16, 8))

    # Compact 6in
    plot_system_performance_boxplot(
        args.csv_file, args.compact_output, figsize=(16, 6),
        label_fontsize=14, tick_fontsize=13, legend_fontsize=13, marker_size=80,
        legend_loc='upper left', legend_ncol=3, legend_markerscale=0.7,
        legend_handlelength=1.2, legend_labelspacing=0.25, legend_borderpad=0.3,
        year_step=2
    )
