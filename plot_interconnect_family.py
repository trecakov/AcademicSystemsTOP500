#
# This script plots interconnect family counts over time using line plot.
# It also outputs a stacked plot and a percentage distribution plot.
#
# To run script 'python3.6 plot_interconnect_family.py'
#

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_interconnect_families(csv_file='interconnect_family_counts_201006_to_202511-modified.csv'):
    
    # Read the data
    df = pd.read_csv(csv_file)
    
    # Convert Date column to datetime for better plotting
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
    
    # Set up the plot
    plt.figure(figsize=(14, 8))
    
    # Colorblind-friendly palette (Okabe-Ito color scheme)
    colors = {
        'Infiniband': '#0173B2',      # Blue
        'Gigabit Ethernet': '#DE8F05', # Orange
        'Omnipath': '#029E73',         # Green
        'Other': '#CC78BC'             # Purple
    }
    
    # Get all columns except Date
    interconnect_columns = [col for col in df.columns if col != 'Date']
    
    # Plot each interconnect family
    for column in interconnect_columns:
        color = colors.get(column, '#000000')  # Default to black if not in palette
        plt.plot(df['Date'], df[column], 
                marker='o', 
                linewidth=2.5, 
                markersize=6,
                label=column,
                color=color,
                alpha=0.9)
    
    # Customize the plot
    plt.xlabel('TOP500 List Year', fontsize=14, fontweight='bold')
    plt.ylabel('Count', fontsize=14, fontweight='bold')
    
    # Add grid for better readability
    plt.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    
    # Format x-axis to show dates nicely
    plt.gcf().autofmt_xdate()
    
    # Add legend
    plt.legend(loc='best', fontsize=12, framealpha=0.9)
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    output_file = 'interconnect_family_plot.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    
    # Display the plot
    plt.show()
    
def plot_stacked_area(csv_file='interconnect_family_counts_201006_to_202511-modified.csv'):
    
    # Read the data
    df = pd.read_csv(csv_file)
    
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
    
    # Set up the plot
    plt.figure(figsize=(14, 8))
    
    # Colorblind-friendly palette
    colors = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC']
    
    # Get all columns except Date
    interconnect_columns = [col for col in df.columns if col != 'Date']
    
    # Create stacked area plot
    plt.stackplot(df['Date'], 
                  [df[col] for col in interconnect_columns],
                  labels=interconnect_columns,
                  colors=colors,
                  alpha=0.8)
    
    # Customize the plot
    plt.xlabel('TOP500 List Year', fontsize=14, fontweight='bold')
    plt.ylabel('Count', fontsize=14, fontweight='bold')
    
    # Add grid
    plt.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')
    
    # Format x-axis
    plt.gcf().autofmt_xdate()
    
    # Add legend
    plt.legend(loc='upper left', fontsize=12, framealpha=0.9)
    
    # Tight layout
    plt.tight_layout()
    
    # Save the plot
    output_file = 'interconnect_family_stacked_plot.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Stacked plot saved to: {output_file}")
    
    # Display the plot
    plt.show()


def plot_percentage_distribution(csv_file='interconnect_family_counts_201006_to_202511.csv'):
    
    # Read the data
    df = pd.read_csv(csv_file)
    
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
    
    # Get all columns except Date
    interconnect_columns = [col for col in df.columns if col != 'Date']
    
    # Calculate percentages
    df_pct = df.copy()
    total = df[interconnect_columns].sum(axis=1)
    for col in interconnect_columns:
        df_pct[col] = (df[col] / total) * 100
    
    # Set up the plot
    plt.figure(figsize=(14, 8))
    
    # Colorblind-friendly palette
    colors = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC']
    
    # Create 100% stacked area plot
    plt.stackplot(df_pct['Date'], 
                  [df_pct[col] for col in interconnect_columns],
                  labels=interconnect_columns,
                  colors=colors,
                  alpha=0.8)
    
    # Customize the plot
    plt.xlabel('TOP500 List Year', fontsize=14, fontweight='bold')
    plt.ylabel('Percentage (%)', fontsize=14, fontweight='bold')
    
    # Set y-axis to 0-100
    plt.ylim(0, 100)
    
    # Add grid
    plt.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')
    
    # Format x-axis
    plt.gcf().autofmt_xdate()
    
    # Add legend
    plt.legend(loc='upper left', fontsize=12, framealpha=0.9)
    
    # Tight layout
    plt.tight_layout()
    
    # Save the plot
    output_file = 'interconnect_family_percentage_plot.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Percentage plot saved to: {output_file}")
    
    # Display the plot
    plt.show()

if __name__ == "__main__":
    csv_file = 'interconnect_family_counts_201006_to_202511-modified.csv'

    # Generate line plot
    plot_interconnect_families(csv_file)

    # Generate stacked area plot
    plot_stacked_area(csv_file)

    # Generate percentage distribution plot
    plot_percentage_distribution(csv_file)
