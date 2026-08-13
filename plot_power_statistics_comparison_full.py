#
# This script plots power statistics over time using box plots with academic and non-academic next to each other.
# It saves both the original full-size plot and a compact 8in version.
#
# To run script python3.6 plot_power_statistics_comparison_full.py power_statistics.csv power_statistics_non_academic.csv
#

import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Extract year and month
def extract_year_month(date_code):
    date_str = str(date_code)
    year = int(date_str[:4]) if len(date_str) >= 4 else None
    month = int(date_str[4:6]) if len(date_str) >= 6 else None
    return year, month


def build_box(row):
    return {
        'whislo': row['Lowest'],   # Minimum power
        'q1': row['Q25'],
        'med': row['Median'],
        'q3': row['Q75'],
        'whishi': row['Highest'],  # Maximum power
        'fliers': []
    }


def plot_power_statistics_boxplot(csv_file, non_academic_file=None,
                                  output_file="power_statistics_boxplot.png",
                                  figsize=(18, 9), label_fontsize=12, tick_fontsize=10,
                                  legend_fontsize=12, marker_size=70,
                                  legend_loc='upper left', legend_ncol=1,
                                  legend_markerscale=1.0, legend_handlelength=2.0,
                                  legend_labelspacing=0.5, legend_borderpad=0.4):

    # Load academic data
    df = pd.read_csv(csv_file)

    years, months = [], []
    for date_code in df['Date']:
        y, m = extract_year_month(date_code)
        years.append(y)
        months.append(m)
    df['Year'] = years
    df['Month'] = months

    unique_year_months = sorted(set(
        (y, m) for y, m in zip(years, months) if y is not None and m is not None
    ))

    bp_data = []            # academic boxes
    top_system_data = []    # academic #1 system
    position_counter = 0
    x_tick_positions = []
    x_tick_labels = []
    year_month_positions = {}
    years_seen = set()

    for year, month in unique_year_months:
        year_month_data = df[(df['Year'] == year) & (df['Month'] == month)]
        for idx, row in year_month_data.iterrows():
            bp_data.append(build_box(row))

            if 'Top_System_Power' in row and pd.notna(row['Top_System_Power']):
                top_system_data.append(row['Top_System_Power'])
            else:
                top_system_data.append(None)

            if (year, month) not in year_month_positions:
                year_month_positions[(year, month)] = position_counter

            if month == 6 and year not in years_seen:
                x_tick_positions.append(position_counter)
                x_tick_labels.append(str(year))
                years_seen.add(year)

            position_counter += 1

    positions_list = list(range(len(bp_data)))

    # Load non-academic data, aligned to academic
    na_bp_data, na_positions = [], []
    na_top_pos, na_top_val = [], []
    have_non_academic = False

    if non_academic_file and os.path.exists(non_academic_file):
        na_df = pd.read_csv(non_academic_file)
        for _, row in na_df.iterrows():
            y, m = extract_year_month(row['Date'])
            pos = year_month_positions.get((y, m))
            if pos is None:
                continue  # no matching academic box to align with
            na_bp_data.append(build_box(row))
            na_positions.append(pos)
            if 'Top_System_Power' in row and pd.notna(row['Top_System_Power']):
                na_top_pos.append(pos)
                na_top_val.append(row['Top_System_Power'])
        have_non_academic = len(na_bp_data) > 0
    elif non_academic_file:
        print(f"Note: '{non_academic_file}' not found - non-academic boxes skipped.")

    # Colors
    # Academic group
    box_color = '#56B4E9'        # Sky blue
    box_edge_color = '#0173B2'   # Dark blue
    median_color = '#009E73'     # Bluish green
    top_system_color = '#D55E00'  # Vermillion
    # Non-academic 
    na_box_color = '#E69F00'     # Amber
    na_box_edge_color = '#B05A00'  # Dark amber
    na_median_color = '#882255'  # Maroon
    na_top_color = '#CC79A7'     # Reddish purple

    # Grouped-box geometry: academic left, non-academic right
    offset = 0.2
    box_width = 0.34

    #Plot
    fig, ax = plt.subplots(figsize=figsize)

    # Academic boxes
    acad_shift = -offset if have_non_academic else 0.0
    acad_positions = [p + acad_shift for p in positions_list]
    ax.bxp(bp_data, positions=acad_positions,
           widths=box_width if have_non_academic else 0.6,
           patch_artist=True, showfliers=False,
           boxprops=dict(facecolor=box_color, alpha=0.7, edgecolor=box_edge_color),
           medianprops=dict(color=median_color, linewidth=2.5),
           whiskerprops=dict(color=box_edge_color, linewidth=1.5),
           capprops=dict(color=box_edge_color, linewidth=1.5))

    # Academic #1 system dots
    if any(y is not None for y in top_system_data):
        vp = [p + acad_shift for p, y in zip(positions_list, top_system_data) if y is not None]
        vy = [y for y in top_system_data if y is not None]
        ax.scatter(vp, vy, marker='o', s=marker_size, color=top_system_color, alpha=0.9,
                   zorder=6, edgecolors='black', linewidths=1)

    # Non-academic boxes
    if have_non_academic:
        na_box_positions = [p + offset for p in na_positions]
        ax.bxp(na_bp_data, positions=na_box_positions, widths=box_width,
               patch_artist=True, showfliers=False,
               boxprops=dict(facecolor=na_box_color, alpha=0.7, edgecolor=na_box_edge_color),
               medianprops=dict(color=na_median_color, linewidth=2.5),
               whiskerprops=dict(color=na_box_edge_color, linewidth=1.5),
               capprops=dict(color=na_box_edge_color, linewidth=1.5))

        # Non-academic #1 system triangles
        if na_top_pos:
            ax.scatter([p + offset for p in na_top_pos], na_top_val, marker='^', s=marker_size,
                       color=na_top_color, alpha=0.9, zorder=7,
                       edgecolors='black', linewidths=1)

    # Axes
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0, fontsize=tick_fontsize)
    ax.tick_params(axis='y', labelsize=tick_fontsize)
    ax.set_xlabel('TOP500 List Year', fontsize=label_fontsize, fontweight='bold')
    ax.set_ylabel('Power Consumption (kW)', fontsize=label_fontsize, fontweight='bold')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3, which='both', linestyle='--', axis='y')

    # Legend
    legend_elements = [
        Patch(facecolor=box_color, edgecolor=box_edge_color, alpha=0.7,
              label='Distribution Q25-Q75 (Academic)'),
        Line2D([0], [0], color=median_color, linewidth=2.5, label='Median (Academic)'),
    ]
    if any(y is not None for y in top_system_data):
        legend_elements.append(
            Line2D([0], [0], marker='o', color='w', markerfacecolor=top_system_color,
                   markersize=10, markeredgecolor='black', markeredgewidth=1,
                   label='#1 System (Academic)', linestyle='None')
        )
    if have_non_academic:
        legend_elements.append(
            Patch(facecolor=na_box_color, edgecolor=na_box_edge_color, alpha=0.7,
                  label='Distribution Q25-Q75 (Non-Academic)')
        )
        legend_elements.append(
            Line2D([0], [0], color=na_median_color, linewidth=2.5, label='Median (Non-Academic)')
        )
        if na_top_pos:
            legend_elements.append(
                Line2D([0], [0], marker='^', color='w', markerfacecolor=na_top_color,
                       markersize=10, markeredgecolor='black', markeredgewidth=1,
                       label='#1 System (Non-Academic)', linestyle='None')
            )

    ax.legend(handles=legend_elements, loc=legend_loc, fontsize=legend_fontsize, framealpha=1,
              ncol=legend_ncol, markerscale=legend_markerscale, handlelength=legend_handlelength,
              labelspacing=legend_labelspacing, borderpad=legend_borderpad)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved as {output_file}")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot academic vs non-academic power consumption statistics as box plots, "
                    "saved as both a full-size PNG and a compact 8in PNG"
    )
    parser.add_argument("csv_file", help="Path to academic power_statistics CSV file")
    parser.add_argument(
        "non_academic_file", nargs="?", default=None,
        help="Path to non-academic power_statistics CSV file (optional)"
    )
    parser.add_argument(
        "--full-output",
        default="power_statistics_boxplot.png",
        help="Path to full-size output PNG file (default: power_statistics_boxplot.png)"
    )
    parser.add_argument(
        "--compact-output",
        default="power_statistics_boxplot_8in.png",
        help="Path to compact (8in-tall) output PNG file (default: power_statistics_boxplot_8in.png)"
    )
    args = parser.parse_args()

    # Full-size plot
    plot_power_statistics_boxplot(
        args.csv_file, args.non_academic_file, args.full_output, figsize=(18, 9)
    )

    # 8in plot
    plot_power_statistics_boxplot(
        args.csv_file, args.non_academic_file, args.compact_output, figsize=(18, 8),
        label_fontsize=14, tick_fontsize=13, legend_fontsize=13, marker_size=65,
        legend_loc='upper left', legend_ncol=3, legend_markerscale=0.9,
        legend_handlelength=1.2, legend_labelspacing=0.25, legend_borderpad=0.3
    )
