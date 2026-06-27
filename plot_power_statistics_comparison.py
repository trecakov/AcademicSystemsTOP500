#
# This script plots power statistics over time using a box plot.
# It overlays, from a second (non-academic) dataset, the #1 non-academic
# system power and the non-academic median on top of the current plot.
#
# To run script 'python3.6 plot_power_statistics.py'
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


def plot_power_statistics_boxplot(csv_file="power_statistics.csv",
                                  non_academic_file="power_statistics_non_academic.csv",
                                  output_file="power_statistics_boxplot_comparison.png"):

    # Load data
    df = pd.read_csv(csv_file)

    # Extract years and months from Date column
    years, months = [], []
    for date_code in df['Date']:
        y, m = extract_year_month(date_code)
        years.append(y)
        months.append(m)

    df['Year'] = years
    df['Month'] = months

    # Group by year and month
    unique_year_months = sorted(set(
        (y, m) for y, m in zip(years, months) if y is not None and m is not None
    ))

    # Prepare data for box plots
    bp_data = []
    top_system_data = []
    position_counter = 0
    x_tick_positions = []
    x_tick_labels = []

    # Map (year, month) -> box position so the non-academic overlay can align
    year_month_positions = {}

    # Group data by year for x-axis labeling
    years_seen = set()

    for year, month in unique_year_months:
        year_month_data = df[(df['Year'] == year) & (df['Month'] == month)]

        for idx, row in year_month_data.iterrows():
            # Add each list as a separate box plot
            box = {
                'whislo': row['Lowest'],   # Minimum power
                'q1': row['Q25'],
                'med': row['Median'],
                'q3': row['Q75'],
                'whishi': row['Highest'],  # Maximum power
                'fliers': []
            }
            bp_data.append(box)

            # Add top system power if available
            if 'Top_System_Power' in row and pd.notna(row['Top_System_Power']):
                top_system_data.append(row['Top_System_Power'])
            else:
                top_system_data.append(None)

            # Record position for this list (first row of a year-month wins)
            if (year, month) not in year_month_positions:
                year_month_positions[(year, month)] = position_counter

            # Only label with year if it's June and we haven't seen this year yet
            if month == 6 and year not in years_seen:
                x_tick_positions.append(position_counter)
                x_tick_labels.append(str(year))
                years_seen.add(year)

            position_counter += 1

    positions_list = list(range(len(bp_data)))

    # Colorblind-friendly palette
    box_color = '#56B4E9'        # Sky blue
    box_edge_color = '#0173B2'   # Dark blue
    median_color = '#009E73'     # Bluish green
    top_system_color = '#D55E00' # Vermillion/red-orange
    # Non-academic overlay colors (distinct from the above)
    na_median_color = '#E69F00'  # Amber
    na_top_color = '#CC79A7'     # Reddish purple

    # Create figure
    fig, ax = plt.subplots(figsize=(16, 8))

    bp = ax.bxp(bp_data, positions=positions_list, widths=0.6,
                patch_artist=True, showfliers=False,
                boxprops=dict(facecolor=box_color, alpha=0.7, edgecolor=box_edge_color),
                medianprops=dict(color=median_color, linewidth=2.5),
                whiskerprops=dict(color=box_edge_color, linewidth=1.5),
                capprops=dict(color=box_edge_color, linewidth=1.5))

    # Overlay the #1 system power as dots
    if any(y is not None for y in top_system_data):
        valid_positions = [p for p, y in zip(positions_list, top_system_data) if y is not None]
        valid_top_power = [y for y in top_system_data if y is not None]

        ax.scatter(valid_positions, valid_top_power, marker='o', s=80,
                   color=top_system_color, alpha=0.9, zorder=6,
                   edgecolors='black', linewidths=1)

    # ------------------------------------------------------------------
    # Overlay non-academic data: #1 non-academic system + non-academic median
    # ------------------------------------------------------------------
    has_na_median = False
    has_na_top = False

    if os.path.exists(non_academic_file):
        na_df = pd.read_csv(non_academic_file)

        na_med_pos, na_med_val = [], []
        na_top_pos, na_top_val = [], []

        for _, row in na_df.iterrows():
            y, m = extract_year_month(row['Date'])
            pos = year_month_positions.get((y, m))
            if pos is None:
                continue  # no matching box in the primary dataset

            if 'Median' in row and pd.notna(row['Median']):
                na_med_pos.append(pos)
                na_med_val.append(row['Median'])

            if 'Top_System_Power' in row and pd.notna(row['Top_System_Power']):
                na_top_pos.append(pos)
                na_top_val.append(row['Top_System_Power'])

        # Non-academic median as a connected line (sorted by position)
        if na_med_pos:
            order = np.argsort(na_med_pos)
            xs = np.array(na_med_pos)[order]
            ys = np.array(na_med_val)[order]
            ax.plot(xs, ys, color=na_median_color, linewidth=2.5,
                    marker='D', markersize=5, alpha=0.9, zorder=5)
            has_na_median = True

        # #1 non-academic system as triangles
        if na_top_pos:
            ax.scatter(na_top_pos, na_top_val, marker='^', s=80,
                       color=na_top_color, alpha=0.9, zorder=7,
                       edgecolors='black', linewidths=1)
            has_na_top = True
    else:
        print(f"Note: '{non_academic_file}' not found - non-academic overlay skipped.")

    # Set up x-axis labels
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0)

    # Labels
    ax.set_xlabel('TOP500 List Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Power Consumption (kW)', fontsize=12, fontweight='bold')

    # Logarithmic y-axis (power spans large range)
    ax.set_yscale('log')

    # Grid
    ax.grid(True, alpha=0.3, which='both', linestyle='--', axis='y')

    # Legend
    legend_elements = [
        Patch(facecolor=box_color, edgecolor=box_edge_color, alpha=0.7, label='Distribution (Q25-Q75) (Academic)'),
        Line2D([0], [0], color=median_color, linewidth=2.5, label='Median (Academic)'),
    ]

    if any(y is not None for y in top_system_data):
        legend_elements.append(
            Line2D([0], [0], marker='o', color='w', markerfacecolor=top_system_color,
                   markersize=10, markeredgecolor='black', markeredgewidth=1,
                   label='#1 System (Academic)', linestyle='None')
        )

    if has_na_median:
        legend_elements.append(
            Line2D([0], [0], color=na_median_color, linewidth=2.5, marker='D',
                   markersize=6, label='Median (Non-Academic)')
        )

    if has_na_top:
        legend_elements.append(
            Line2D([0], [0], marker='^', color='w', markerfacecolor=na_top_color,
                   markersize=10, markeredgecolor='black', markeredgewidth=1,
                   label='#1 System (Non-Academic)', linestyle='None')
        )

    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.9)

    # Tight layout
    plt.tight_layout()

    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved as {output_file}")

    # Show plot
    plt.show()


if __name__ == "__main__":
    plot_power_statistics_boxplot()
