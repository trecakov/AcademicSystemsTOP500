#
# This script plots total core and accelerators core count from 2011-2025 using box plot.
#
# To run script 'python3.6 plot_age.py'
#

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

def plot_accelerator_statistics(csv_file="accelerator_statistics.csv", 
                                output_file="core_statistics.png"):
   
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
    
    # Colorblind-friendly palette
    accel_box_color = '#56B4E9'      # Sky blue for accelerator cores
    accel_edge_color = '#0173B2'     # Dark blue
    total_box_color = '#E69F00'      # Orange for total cores
    total_edge_color = '#D55E00'     # Dark orange
    median_color = '#009E73'         # Bluish green
    top_with_accel_color = '#D55E00' # Vermillion/red-orange (has accelerator)
    top_no_accel_color = '#CC79A7'   # Reddish purple (no accelerator)
    
    # Prepare data for both box plots
    accel_bp_data = []
    total_bp_data = []
    top_with_accel = []
    top_without_accel = []
    
    position_counter = 0
    accel_positions = []
    total_positions = []
    x_tick_positions = []
    x_tick_labels = []
    years_seen = set()
    
    for year, month in unique_year_months:
        year_month_data = df[(df['Year'] == year) & (df['Month'] == month)]
        
        for idx, row in year_month_data.iterrows():
            # Accelerator cores box (offset left)
            if pd.notna(row['Accel_Cores_Median']):
                accel_box = {
                    'whislo': row['Accel_Cores_Best'],
                    'q1': row['Accel_Cores_Q25'],
                    'med': row['Accel_Cores_Median'],
                    'q3': row['Accel_Cores_Q75'],
                    'whishi': row['Accel_Cores_Worst'],
                    'fliers': []
                }
                accel_bp_data.append(accel_box)
                accel_positions.append(position_counter - 0.2)  # Offset left
            
            # Total cores box (offset right)
            if pd.notna(row['Total_Cores_Median']):
                total_box = {
                    'whislo': row['Total_Cores_Best'],
                    'q1': row['Total_Cores_Q25'],
                    'med': row['Total_Cores_Median'],
                    'q3': row['Total_Cores_Q75'],
                    'whishi': row['Total_Cores_Worst'],
                    'fliers': []
                }
                total_bp_data.append(total_box)
                total_positions.append(position_counter + 0.2)  # Offset right
            
            # Track top system for total cores
            if pd.notna(row['Top_System_Total_Cores']):
                if row['Top_System_Has_Accelerator']:
                    top_with_accel.append((position_counter + 0.2, row['Top_System_Total_Cores']))
                else:
                    top_without_accel.append((position_counter + 0.2, row['Top_System_Total_Cores']))
            
            # X-axis labels
            if month == 6 and year not in years_seen:
                x_tick_positions.append(position_counter)
                x_tick_labels.append(str(year))
                years_seen.add(year)
            
            position_counter += 1
    
    # Create single figure
    fig, ax = plt.subplots(figsize=(18, 8))
    
    # Plot accelerator cores boxes
    if len(accel_bp_data) > 0:
        bp_accel = ax.bxp(accel_bp_data, positions=accel_positions, widths=0.35,
                    patch_artist=True, showfliers=False,
                    boxprops=dict(facecolor=accel_box_color, alpha=0.7, edgecolor=accel_edge_color, linewidth=1.5),
                    medianprops=dict(color=median_color, linewidth=2),
                    whiskerprops=dict(color=accel_edge_color, linewidth=1.5),
                    capprops=dict(color=accel_edge_color, linewidth=1.5))
    
    # Plot total cores boxes
    if len(total_bp_data) > 0:
        bp_total = ax.bxp(total_bp_data, positions=total_positions, widths=0.35,
                    patch_artist=True, showfliers=False,
                    boxprops=dict(facecolor=total_box_color, alpha=0.7, edgecolor=total_edge_color, linewidth=1.5),
                    medianprops=dict(color=median_color, linewidth=2),
                    whiskerprops=dict(color=total_edge_color, linewidth=1.5),
                    capprops=dict(color=total_edge_color, linewidth=1.5))
    
    # Plot top systems with accelerators (circles)
    if len(top_with_accel) > 0:
        pos_with = [pos for pos, val in top_with_accel]
        val_with = [val for pos, val in top_with_accel]
        ax.scatter(pos_with, val_with, marker='o', s=100, color=top_with_accel_color, 
                   alpha=0.9, zorder=6, edgecolors='black', linewidths=1.5)
    
    # Plot top systems without accelerators (squares)
    if len(top_without_accel) > 0:
        pos_without = [pos for pos, val in top_without_accel]
        val_without = [val for pos, val in top_without_accel]
        ax.scatter(pos_without, val_without, marker='s', s=100, color=top_no_accel_color, 
                   alpha=0.9, zorder=6, edgecolors='black', linewidths=1.5)
    
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0)
    ax.set_xlabel('TOP500 List Year', fontsize=13, fontweight='bold')
    ax.set_ylabel('Core Count', fontsize=13, fontweight='bold')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3, which='both', linestyle='--', axis='y')
    
    # Create legend
    legend_elements = [
        Patch(facecolor=accel_box_color, edgecolor=accel_edge_color, alpha=0.7, label='Accelerator Cores (Q25-Q75)'),
        Patch(facecolor=total_box_color, edgecolor=total_edge_color, alpha=0.7, label='Total Cores (Q25-Q75)'),
        Line2D([0], [0], color=median_color, linewidth=2, label='Median'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=top_with_accel_color,
               markersize=11, markeredgecolor='black', markeredgewidth=1.5, label='#1 System (with accelerators)', linestyle='None'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor=top_no_accel_color,
               markersize=11, markeredgecolor='black', markeredgewidth=1.5, label='#1 System (without accelerators)', linestyle='None')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nCombined plot saved as {output_file}")
    plt.show()

if __name__ == "__main__":
    plot_accelerator_statistics()
