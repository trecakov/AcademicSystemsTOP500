#
# This script plots energy efficiency from 2015-2026 using box plots.
#
# To run script 'python3.6 plot_energy_efficiency-box-plot.py energy_efficiency_quantiles_academic.csv energy_efficiency_quantiles_non_academic.csv'
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

# Convert TFlops/kw to TFlops/W
def prepare_df(csv_file, ymin=2015, ymax=2026):
    df = pd.read_csv(csv_file)

    years, months = [], []
    for date_code in df['Date']:
        y, m = extract_year_month(date_code)
        years.append(y)
        months.append(m)
    df['Year'] = years
    df['Month'] = months

    # Convert efficiency from TFlops/kW to TFlops/W (divide by 1000)
    conversions = [
        ('Max_Efficiency', 'Max_Efficiency_W'),
        ('Q75', 'Q75_W'),
        ('Median', 'Median_W'),
        ('Q25', 'Q25_W'),
        ('Min_Efficiency', 'Min_Efficiency_W'),
        ('Top_System_Efficiency', 'Top_System_Efficiency_W'),
    ]
    for src, dst in conversions:
        df[dst] = df[src] / 1000.0

    df = df[(df['Year'] >= ymin) & (df['Year'] <= ymax)]
    return df


def build_box(row):
    return {
        'whislo': row['Min_Efficiency_W'],
        'q1': row['Q25_W'],
        'med': row['Median_W'],
        'q3': row['Q75_W'],
        'whishi': row['Max_Efficiency_W'],
        'fliers': []
    }


def plot_energy_efficiency_boxplot(csv_file, non_academic_file=None,
                                   output_file="energy_efficiency_boxplot.png",
                                   figsize=(18, 9), label_fontsize=12, tick_fontsize=10,
                                   legend_fontsize=12, marker_size=7, line_width=2.5,
                                   legend_loc='upper left', legend_ncol=1,
                                   legend_markerscale=1.0, legend_handlelength=2.0,
                                   legend_labelspacing=0.5, legend_borderpad=0.4):

    # Load academic data
    df = prepare_df(csv_file)
    if len(df) == 0:
        print("No academic data found for years 2015-2026")
        return
    print(f"Filtered academic data to {len(df)} records between 2015-2026")

    unique_year_months = sorted(set(
        (y, m) for y, m in zip(df['Year'], df['Month']) if y is not None and m is not None
    ))

    bp_data = []
    top_system_data = []
    position_counter = 0
    x_tick_positions = []
    x_tick_labels = []
    year_month_positions = {}
    years_seen = set()

    for year, month in unique_year_months:
        year_month_data = df[(df['Year'] == year) & (df['Month'] == month)]
        for idx, row in year_month_data.iterrows():
            bp_data.append(build_box(row))
            top_system_data.append(row['Top_System_Efficiency_W'])

            if (year, month) not in year_month_positions:
                year_month_positions[(year, month)] = position_counter

            if month == 6 and year not in years_seen:
                x_tick_positions.append(position_counter)
                x_tick_labels.append(str(year))
                years_seen.add(year)

            position_counter += 1

    positions_list = list(range(len(bp_data)))

    # Load non-academic data aligned with academic
    na_bp_data, na_positions = [], []
    na_top_pos, na_top_val = [], []
    have_non_academic = False

    if non_academic_file and os.path.exists(non_academic_file):
        na_df = prepare_df(non_academic_file)
        for _, row in na_df.iterrows():
            pos = year_month_positions.get((row['Year'], row['Month']))
            if pos is None:
                continue
            na_bp_data.append(build_box(row))
            na_positions.append(pos)
            na_top_pos.append(pos)
            na_top_val.append(row['Top_System_Efficiency_W'])
        have_non_academic = len(na_bp_data) > 0
        if have_non_academic:
            print(f"Filtered non-academic data to {len(na_bp_data)} aligned records")
    elif non_academic_file:
        print(f"Note: '{non_academic_file}' not found - non-academic boxes skipped.")

    # Colors
    # Academic group
    box_color = '#56B4E9'        # Sky blue
    box_edge_color = '#0173B2'   # Dark blue
    median_color = '#009E73'     # Bluish green
    top_system_color = '#D55E00' # Vermillion
    # Non-academic group
    na_box_color = '#E69F00'     # Amber
    na_box_edge_color = '#B05A00'  # Dark amber
    na_median_color = '#882255'  # Maroon
    na_top_color = '#CC79A7'     # Reddish purple

    offset = 0.2
    box_width = 0.34

    # Plot
    fig, ax = plt.subplots(figsize=figsize)

    acad_shift = -offset if have_non_academic else 0.0
    acad_positions = [p + acad_shift for p in positions_list]

    ax.bxp(bp_data, positions=acad_positions,
           widths=box_width if have_non_academic else 0.6,
           patch_artist=True, showfliers=False,
           boxprops=dict(facecolor=box_color, alpha=0.7, edgecolor=box_edge_color),
           medianprops=dict(color=median_color, linewidth=2.5),
           whiskerprops=dict(color=box_edge_color, linewidth=1.5),
           capprops=dict(color=box_edge_color, linewidth=1.5))

    # Academic #1 system as a line
    ax.plot(acad_positions, top_system_data, marker='o', linewidth=line_width, markersize=marker_size,
            color=top_system_color, alpha=0.9, zorder=5)

    # Non-academic boxes + #1 system line
    if have_non_academic:
        na_box_positions = [p + offset for p in na_positions]
        ax.bxp(na_bp_data, positions=na_box_positions, widths=box_width,
               patch_artist=True, showfliers=False,
               boxprops=dict(facecolor=na_box_color, alpha=0.7, edgecolor=na_box_edge_color),
               medianprops=dict(color=na_median_color, linewidth=2.5),
               whiskerprops=dict(color=na_box_edge_color, linewidth=1.5),
               capprops=dict(color=na_box_edge_color, linewidth=1.5))

        order = np.argsort(na_top_pos)
        na_x = (np.array(na_top_pos)[order] + offset)
        na_y = np.array(na_top_val)[order]
        ax.plot(na_x, na_y, marker='^', linewidth=line_width, markersize=marker_size,
                color=na_top_color, alpha=0.9, zorder=6)

    # Axes
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0, fontsize=tick_fontsize)
    ax.tick_params(axis='y', labelsize=tick_fontsize)
    ax.set_xlabel('TOP500 List Year', fontsize=label_fontsize, fontweight='bold')
    ax.set_ylabel('Energy Efficiency (TFlops/Watt)', fontsize=label_fontsize, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    # Legend
    legend_elements = [
        Patch(facecolor=box_color, edgecolor=box_edge_color, alpha=0.7,
              label='Distribution Q25-Q75 (Academic)'),
        Line2D([0], [0], color=median_color, linewidth=2.5, label='Median (Academic)'),
        Line2D([0], [0], color=top_system_color, linewidth=2.5, marker='o', markersize=7,
               label='#1 System (Academic)'),
    ]
    if have_non_academic:
        legend_elements.append(
            Patch(facecolor=na_box_color, edgecolor=na_box_edge_color, alpha=0.7,
                  label='Distribution Q25-Q75 (Non-Academic)')
        )
        legend_elements.append(
            Line2D([0], [0], color=na_median_color, linewidth=2.5, label='Median (Non-Academic)')
        )
        legend_elements.append(
            Line2D([0], [0], color=na_top_color, linewidth=2.5, marker='^', markersize=7,
                   label='#1 System (Non-Academic)')
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
        description="Plot academic vs non-academic energy efficiency (TFlops/Watt) as box "
                    "plots, saved as both a full-size PNG and a compact 6in PNG"
    )
    parser.add_argument("csv_file", help="Path to academic energy_efficiency_quantiles CSV file")
    parser.add_argument(
        "non_academic_file", nargs="?", default=None,
        help="Path to non-academic energy_efficiency_quantiles CSV file (optional)"
    )
    parser.add_argument(
        "--full-output",
        default="energy_efficiency_boxplot.png",
        help="Path to full-size output PNG file (default: energy_efficiency_boxplot.png)"
    )
    parser.add_argument(
        "--compact-output",
        default="energy_efficiency_boxplot_6in.png",
        help="Path to compact 6in output PNG file (default: energy_efficiency_boxplot_6in.png)"
    )
    args = parser.parse_args()

    # Full-size
    plot_energy_efficiency_boxplot(
        args.csv_file, args.non_academic_file, args.full_output, figsize=(18, 9)
    )

    # Compact 6in
    plot_energy_efficiency_boxplot(
        args.csv_file, args.non_academic_file, args.compact_output, figsize=(18, 6),
        label_fontsize=14, tick_fontsize=13, legend_fontsize=13, marker_size=9, line_width=2.2,
        legend_loc='upper left', legend_ncol=3, legend_markerscale=0.9,
        legend_handlelength=1.2, legend_labelspacing=0.25, legend_borderpad=0.3
    )
