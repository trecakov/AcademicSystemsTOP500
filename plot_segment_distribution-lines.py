#
# This script plots segment distribution over years using stacked area chart.
# It also outputs a percentage plot.
#
# To run script 'python3.6 plot_segment_distribution-lines.py'
#

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

def plot_segment_distribution(csv_file="segment_distribution.csv", 
                              output_file="segment_distribution.png"):
    
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
    
    # Get all segment columns
    segment_cols = [col for col in df.columns if col.startswith('Segment_')]
    
    if len(segment_cols) == 0:
        print("No segment columns found!")
        return
    
    # Create clean segment names for labels
    segment_names = [col.replace('Segment_', '').replace('_', ' ') for col in segment_cols]
    
    # Prepare data for plotting (use list index as x-axis)
    x = np.arange(len(df))
    
    # Extract segment data
    segment_data = []
    for col in segment_cols:
        segment_data.append(df[col].values)
    
    # Colorblind-friendly palette (Paul Tol's vibrant scheme)
    colors = [
        '#0173B2',  # Blue
        '#DE8F05',  # Orange
        '#029E73',  # Cyan/Green
        '#CC78BC',  # Pink/Purple
        '#CA9161',  # Brown
        '#FBAFE4',  # Light pink
        '#949494',  # Grey
        '#ECE133',  # Yellow
        '#56B4E9',  # Sky blue
    ]
    
    # Extend colors if needed
    while len(colors) < len(segment_cols):
        colors.append(f'#{np.random.randint(0, 0xFFFFFF):06x}')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(18, 10))
    
    # Create line plot for each segment
    for i, (data, name) in enumerate(zip(segment_data, segment_names)):
        ax.plot(x, data, label=name, color=colors[i], linewidth=2.5, marker='o', 
                markersize=4, alpha=0.9)
    
    # Set up x-axis with years
    # Show year labels only for June lists
    unique_year_months = sorted(set([(y, m) for y, m in zip(years, months) if y is not None and m is not None]))
    x_tick_positions = []
    x_tick_labels = []
    years_seen = set()
    
    for i, (year, month) in enumerate(unique_year_months):
        if month == 6 and year not in years_seen:
            x_tick_positions.append(i)
            x_tick_labels.append(str(year))
            years_seen.add(year)
    
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0)
    
    # Labels and title
    ax.set_xlabel('TOP500 List Year', fontsize=13, fontweight='bold')
    ax.set_ylabel('Number of Systems', fontsize=13, fontweight='bold')
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Add legend
    ax.legend(loc='upper left', fontsize=14, framealpha=1, ncol=1)
    
    # Set y-axis to start at 0
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved as {output_file}")
    plt.show()

def plot_segment_percentage(csv_file="segment_distribution.csv", 
                            output_file="segment_percentage.png"):
    
    # Load data
    df = pd.read_csv(csv_file)
    
    # Extract years and months
    years = []
    months = []
    for date_code in df['Date']:
        date_str = str(date_code)
        if len(date_str) >= 4:
            years.append(int(date_str[:4]))
        else:
            years.append(None)
        if len(date_str) >= 6:
            months.append(int(date_str[4:6]))
        else:
            months.append(None)
    
    df['Year'] = years
    df['Month'] = months
    
    # Get all segment columns
    segment_cols = [col for col in df.columns if col.startswith('Segment_')]
    
    if len(segment_cols) == 0:
        print("No segment columns found!")
        return
    
    # Calculate percentages
    segment_data_pct = []
    for col in segment_cols:
        percentage = (df[col] / df['Total_Systems']) * 100
        segment_data_pct.append(percentage.values)
    
    # Create clean segment names
    segment_names = [col.replace('Segment_', '').replace('_', ' ') for col in segment_cols]
    
    # Prepare x-axis
    x = np.arange(len(df))
    
    # Colorblind-friendly palette
    colors = [
        '#0173B2',  # Blue
        '#DE8F05',  # Orange
        '#029E73',  # Cyan/Green
        '#CC78BC',  # Pink/Purple
        '#CA9161',  # Brown
        '#FBAFE4',  # Light pink
        '#949494',  # Grey
        '#ECE133',  # Yellow
        '#56B4E9',  # Sky blue
    ]
    
    while len(colors) < len(segment_cols):
        colors.append(f'#{np.random.randint(0, 0xFFFFFF):06x}')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(18, 10))
    
    # Create line plot for each segment (percentage)
    for i, (data, name) in enumerate(zip(segment_data_pct, segment_names)):
        ax.plot(x, data, label=name, color=colors[i], linewidth=2.5, marker='o', 
                markersize=4, alpha=0.9)
    
    # Set up x-axis with years
    unique_year_months = sorted(set([(y, m) for y, m in zip(years, months) if y is not None and m is not None]))
    x_tick_positions = []
    x_tick_labels = []
    years_seen = set()
    
    for i, (year, month) in enumerate(unique_year_months):
        if month == 6 and year not in years_seen:
            x_tick_positions.append(i)
            x_tick_labels.append(str(year))
            years_seen.add(year)
    
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0)
    
    # Labels and title
    ax.set_xlabel('TOP500 List Year', fontsize=13, fontweight='bold')
    ax.set_ylabel('Percentage of Systems (%)', fontsize=13, fontweight='bold')
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Add legend
    ax.legend(loc='upper left', fontsize=14, framealpha=1, ncol=1)
    
    # Set y-axis limits
    ax.set_ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPercentage plot saved as {output_file}")
    plt.show()

if __name__ == "__main__":
    # Create both absolute count and percentage plots
    plot_segment_distribution()
    plot_segment_percentage()
