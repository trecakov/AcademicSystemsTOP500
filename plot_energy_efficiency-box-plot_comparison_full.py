#
# This script plots energy efficiency from 2015-2025 using box plots.
# It draws side-by-side box-and-whisker plots for two populations on the same
# graph -- Academic (from energy_efficiency_quantiles.csv) and Non-Academic
# (from energy_efficiency_quantiles_non_academic.csv) -- and overlays the
# #1 system efficiency of each population.
#
# To run script 'python3.6 plot_energy_efficiency-box-plot.py'
#

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


def extract_year_month(date_code):
    """Return (year, month) parsed from a YYYYMM-style Date code."""
    date_str = str(date_code)
    year = int(date_str[:4]) if len(date_str) >= 4 else None
    month = int(date_str[4:6]) if len(date_str) >= 6 else None
    return year, month


def prepare_df(csv_file, ymin=2015, ymax=2025):
    """Load a quantiles CSV, convert TFlops/kW -> TFlops/W, and filter years."""
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
    """Build a matplotlib bxp box dict from a (converted) quantiles row."""
    return {
        'whislo': row['Min_Efficiency_W'],
        'q1': row['Q25_W'],
        'med': row['Median_W'],
        'q3': row['Q75_W'],
        'whishi': row['Max_Efficiency_W'],
        'fliers': []
    }


def plot_energy_efficiency_boxplot(csv_file="energy_efficiency_quantiles.csv",
                                   non_academic_file="energy_efficiency_quantiles_non_academic.csv",
                                   output_file="energy_efficiency_boxplot.png"):

    # ---- Load academic (primary) data ----
    df = prepare_df(csv_file)
    if len(df) == 0:
        print("No academic data found for years 2015-2025")
        return
    print(f"Filtered academic data to {len(df)} records between 2015-2025")

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

    # ---- Load non-academic data, aligned to academic positions ----
    na_bp_data, na_positions = [], []
    na_top_pos, na_top_val = [], []
    have_non_academic = False

    if os.path.exists(non_academic_file):
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
    else:
        print(f"Note: '{non_academic_file}' not found - non-academic boxes skipped.")

    # ---- Colors (colorblind-friendly) ----
    # Academic group (cool)
    box_color = '#56B4E9'        # Sky blue
    box_edge_color = '#0173B2'   # Dark blue
    median_color = '#009E73'     # Bluish green
    top_system_color = '#D55E00' # Vermillion
    # Non-academic group (warm)
    na_box_color = '#E69F00'     # Amber
    na_box_edge_color = '#B05A00'  # Dark amber
    na_median_color = '#882255'  # Maroon
    na_top_color = '#CC79A7'     # Reddish purple

    # Grouped-box geometry
    offset = 0.2
    box_width = 0.34

    # ---- Plot ----
    fig, ax = plt.subplots(figsize=(18, 9))

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
    ax.plot(acad_positions, top_system_data, marker='o', linewidth=2.5, markersize=7,
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
        ax.plot(na_x, na_y, marker='^', linewidth=2.5, markersize=7,
                color=na_top_color, alpha=0.9, zorder=6)

    # ---- Axes ----
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0)
    ax.set_xlabel('TOP500 List Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Energy Efficiency (TFlops/Watt)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    # ---- Legend ----
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

    ax.legend(handles=legend_elements, loc='upper left', fontsize=12, framealpha=1)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved as {output_file}")
    plt.show()


if __name__ == "__main__":
    plot_energy_efficiency_boxplot()
