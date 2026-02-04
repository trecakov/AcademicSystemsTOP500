#
# This script plots performance development over time.
# The plot displays best, worst and sum of Rmax values.
#
# To run script 'python3.6 plot_performance_development.py'
#


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

def plot_rmax_statistics(csv_file="rmax_statistics.csv", output_file="rmax_trends.png"):
    
    # Load data
    df = pd.read_csv(csv_file)
    
    # Extract years from List column - handle different formats
    years = []
    for list_name in df['List']:
        list_str = str(list_name)
        # Try to find year pattern (4 consecutive digits starting with 19 or 20)
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
    
    # Create x-axis positions
    x = np.arange(len(df))
    
    # Create figure with logarithmic y-axis
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Colorblind-friendly palette
    first_color = '#009E73'    # Bluish green
    last_color = '#0173B2'     # Blue
    sum_color = '#D55E00'      # Vermillion/red-orange
    
    # Plot the three metrics with colorblind-friendly colors
    ax.plot(x, df['Best'].values, marker='o', linewidth=2, markersize=6,
            label='First', color=first_color, alpha=0.8)
    ax.plot(x, df['Worst'].values, marker='s', linewidth=2, markersize=6,
            label='Last', color=last_color, alpha=0.8)
    ax.plot(x, df['Sum'].values, marker='^', linewidth=2, markersize=6,
            label='Sum (All Academic Systems)', color=sum_color, alpha=0.8)
    
    # Set logarithmic scale for y-axis
    ax.set_yscale('log')
    
    # Set up x-axis with years
    # Get unique years for labels
    unique_years = sorted(set([y for y in years if y is not None]))
    
    # Show every 2-3 years to avoid crowding
    step = max(1, len(unique_years) // 15)
    selected_years = unique_years[::step]
    
    # Find positions for these years
    year_positions = []
    for year in selected_years:
        # Find first occurrence of this year
        idx = next((i for i, y in enumerate(years) if y == year), None)
        if idx is not None:
            year_positions.append(idx)
    
    ax.set_xticks(year_positions)
    ax.set_xticklabels(selected_years, rotation=45)
    
    # Labels and title
    ax.set_xlabel('TOP500 List Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Rmax (TFlop/s)', fontsize=12, fontweight='bold')
    
    # Add grid
    ax.grid(True, alpha=0.3, which='both', linestyle='--')
    
    # Add legend
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    
    # Tight layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved as {output_file}")
    
    # Show plot
    plt.show()

if __name__ == "__main__":
    plot_rmax_statistics()
