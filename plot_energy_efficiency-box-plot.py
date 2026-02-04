#
# This script plots energy efficiency from 2015-2025 using box plot.
#
# To run script 'python3.6 plot_energy_efficiency-box-plot.py'
#

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.patches import Patch

def plot_energy_efficiency_boxplot(csv_file="energy_efficiency_quantiles.csv", output_file="energy_efficiency_boxplot.png"):
    
    # Load data
    df = pd.read_csv(csv_file)

    # Extract years from Date column
    years = []
    for date_code in df['Date']:
        date_str = str(date_code)
        if len(date_str) >= 4:
            year = int(date_str[:4])
            years.append(year)
        else:
            years.append(None)

    df['Year'] = years

    # Convert efficiency from TFlops/kW to TFlops/W (divide by 1000)
    df['Max_Efficiency_W'] = df['Max_Efficiency'] / 1000.0
    df['Q75_W'] = df['Q75'] / 1000.0
    df['Median_W'] = df['Median'] / 1000.0
    df['Q25_W'] = df['Q25'] / 1000.0
    df['Min_Efficiency_W'] = df['Min_Efficiency'] / 1000.0
    df['Top_System_Efficiency_W'] = df['Top_System_Efficiency'] / 1000.0

    # Extract month from Date column
    months = []
    for date_code in df['Date']:
        date_str = str(date_code)
        if len(date_str) >= 6:
            month = int(date_str[4:6])
            months.append(month)
        else:
            months.append(None)

    df['Month'] = months

    # Filter data for years 2015-2025
    df = df[(df['Year'] >= 2015) & (df['Year'] <= 2025)]

    if len(df) == 0:
        print("No data found for years 2015-2025")
        return

    print(f"Filtered to {len(df)} records between 2015-2025")

    # Group by year and month (keep both 06 and 11)
    unique_year_months = sorted(set([(y, m) for y, m in zip(df['Year'], df['Month']) if y is not None and m is not None]))

    # Prepare data for box plots and top system line
    bp_data = []
    top_system_data = []
    position_counter = 0
    x_tick_positions = []
    x_tick_labels = []

    # Group data by year for x-axis labeling
    years_seen = set()

    for year, month in unique_year_months:
        year_month_data = df[(df['Year'] == year) & (df['Month'] == month)]

        for idx, row in year_month_data.iterrows():
            # Add each list as a separate box plot
            box = {
                'whislo': row['Min_Efficiency_W'],
                'q1': row['Q25_W'],
                'med': row['Median_W'],
                'q3': row['Q75_W'],
                'whishi': row['Max_Efficiency_W'],
                'fliers': []
            }
            bp_data.append(box)
            top_system_data.append(row['Top_System_Efficiency_W'])

            # Only label with year if it's June and we haven't seen this year yet
            if month == 6 and year not in years_seen:
                x_tick_positions.append(position_counter)
                x_tick_labels.append(str(year))
                years_seen.add(year)

            position_counter += 1

    positions_list = list(range(len(bp_data)))
    
    # Colorblind-friendly palette
    box_color = '#56B4E9'      # Sky blue
    box_edge_color = '#0173B2' # Dark blue
    median_color = '#009E73'   # Bluish green
    top_system_color = '#D55E00' # Vermillion/red-orange
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 8))

    bp = ax.bxp(bp_data, positions=positions_list, widths=0.6,
                patch_artist=True, showfliers=False,
                boxprops=dict(facecolor=box_color, alpha=0.7, edgecolor=box_edge_color),
                medianprops=dict(color=median_color, linewidth=2.5),
                whiskerprops=dict(color=box_edge_color, linewidth=1.5),
                capprops=dict(color=box_edge_color, linewidth=1.5))

    # Overlay the #1 system efficiency as a line
    ax.plot(positions_list, top_system_data, marker='o', linewidth=2.5, markersize=7,
            label='#1 System', color=top_system_color, alpha=0.9, zorder=5)

    # Set up x-axis labels - only show year labels at designated positions
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0)

    # Labels and title
    ax.set_xlabel('TOP500 List Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Energy Efficiency (TFlops/Watt)', fontsize=12, fontweight='bold')
    # ax.set_title('Energy Efficiency Development', fontsize=14, fontweight='bold')

    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    # Add legend
    legend_elements = [
        Patch(facecolor=box_color, edgecolor=box_edge_color, alpha=0.7, label='Distribution (Q25-Q75)'),
        plt.Line2D([0], [0], color=median_color, linewidth=2.5, label='Median'),
        plt.Line2D([0], [0], color=top_system_color, linewidth=2.5, marker='o', markersize=7, label='#1 System')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.9)

    # Tight layout
    plt.tight_layout()

    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved as {output_file}")

    # Show plot
    plt.show()

if __name__ == "__main__":
    plot_energy_efficiency_boxplot()
