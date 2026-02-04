#
# This script plots power statistics ove time using box plot.
#
# To run script 'python3.6 plot_power_statistics.py'
#


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.patches import Patch

def plot_power_statistics_boxplot(csv_file="power_statistics.csv", output_file="power_statistics_boxplot.png"):
    
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
    
    # Group by year and month
    unique_year_months = sorted(set([(y, m) for y, m in zip(years, months) if y is not None and m is not None]))
    
    # Prepare data for box plots
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
    
    # Overlay the #1 system power as dots
    if any(y is not None for y in top_system_data):
        valid_positions = [p for p, y in zip(positions_list, top_system_data) if y is not None]
        valid_top_power = [y for y in top_system_data if y is not None]
        
        ax.scatter(valid_positions, valid_top_power, marker='o', s=80,
                   color=top_system_color, alpha=0.9, zorder=6, edgecolors='black', linewidths=1)
    
    # Set up x-axis labels
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0)
    
    # Labels and title
    ax.set_xlabel('TOP500 List Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Power Consumption (kW)', fontsize=12, fontweight='bold')
    
    # Use logarithmic scale for y-axis (power spans large range)
    ax.set_yscale('log')
    
    # Add grid
    ax.grid(True, alpha=0.3, which='both', linestyle='--', axis='y')
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor=box_color, edgecolor=box_edge_color, alpha=0.7, label='Distribution (Q25-Q75)'),
        plt.Line2D([0], [0], color=median_color, linewidth=2.5, label='Median')
    ]
    
    # Add #1 system to legend if data exists
    if any(y is not None for y in top_system_data):
        legend_elements.append(
            Line2D([0], [0], marker='o', color='w', markerfacecolor=top_system_color,
                   markersize=10, markeredgecolor='black', markeredgewidth=1, label='#1 System', linestyle='None')
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
