#
# This script plots segment distribution (number of systems) over the years as a line plot and a 2 sizes.
#
# To run script python3.6 plot_segment_distribution-lines.py segment_distribution_stats.csv
#

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Single-column sizing
COLUMN_FIGSIZE = (3.5, 2.8)
COLUMN_LABEL_FONTSIZE = 9
COLUMN_TICK_FONTSIZE = 8
COLUMN_LEGEND_FONTSIZE = 8
COLUMN_LINEWIDTH = 1.2
COLUMN_MARKERSIZE = 2.5

# Full-size sizing
FULL_FIGSIZE = (18, 10)
FULL_LABEL_FONTSIZE = 13
FULL_TICK_FONTSIZE = 11
FULL_LEGEND_FONTSIZE = 14
FULL_LINEWIDTH = 2.5
FULL_MARKERSIZE = 4

# Extract year and month
def extract_year_month(df):
    years = []
    months = []
    for date_code in df['Date']:
        date_str = str(date_code)
        years.append(int(date_str[:4]) if len(date_str) >= 4 else None)
        months.append(int(date_str[4:6]) if len(date_str) >= 6 else None)
    return years, months

# Set xticks
def set_year_xticks(ax, years, months, fontsize, year_interval=1):
    unique_year_months = sorted(set(
        (y, m) for y, m in zip(years, months) if y is not None and m is not None
    ))
    x_tick_positions = []
    x_tick_labels = []
    years_seen = set()

    for i, (year, month) in enumerate(unique_year_months):
        if month == 6 and year not in years_seen:
            years_seen.add(year)
            if (year - min(y for y, m in unique_year_months if m == 6)) % year_interval == 0:
                x_tick_positions.append(i)
                x_tick_labels.append(str(year))

    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0, fontsize=fontsize)

# Color palet
def get_segment_colors(n):
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
    while len(colors) < n:
        colors.append(f'#{np.random.randint(0, 0xFFFFFF):06x}')
    return colors

# Plot segment distribution over years
def plot_segment_distribution(csv_file, output_file, figsize, label_fontsize,
                               tick_fontsize, legend_fontsize, linewidth, markersize,
                               year_interval=1, legend_loc='upper left',
                               legend_ncol=1, legend_markerscale=1.0,
                               legend_handlelength=2.0, legend_labelspacing=0.5,
                               legend_borderpad=0.4):

    # Load data
    df = pd.read_csv(csv_file)

    years, months = extract_year_month(df)
    df['Year'] = years
    df['Month'] = months

    # Get all segment columns
    segment_cols = [col for col in df.columns if col.startswith('Segment_')]

    if len(segment_cols) == 0:
        print("No segment columns found!")
        return

    # Create segment names
    segment_names = [col.replace('Segment_', '').replace('_', ' ') for col in segment_cols]

    # Prepare data for plotting
    x = np.arange(len(df))

    # Extract segment data
    segment_data = [df[col].values for col in segment_cols]

    colors = get_segment_colors(len(segment_cols))

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create line plot for each segment
    for data, name, color in zip(segment_data, segment_names, colors):
        ax.plot(x, data, label=name, color=color, linewidth=linewidth, marker='o',
                markersize=markersize, alpha=0.9)

    # Set up x-axis with years
    set_year_xticks(ax, years, months, fontsize=tick_fontsize, year_interval=year_interval)
    ax.tick_params(axis='y', labelsize=tick_fontsize)

    # Labels
    ax.set_xlabel('TOP500 List Year', fontsize=label_fontsize, fontweight='bold')
    ax.set_ylabel('Number of Systems', fontsize=label_fontsize, fontweight='bold')

    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    # Set y-axis
    ax.set_ylim(bottom=0)

    # Add legend
    ax.legend(
        loc=legend_loc, fontsize=legend_fontsize, framealpha=1, ncol=legend_ncol,
        markerscale=legend_markerscale, handlelength=legend_handlelength,
        labelspacing=legend_labelspacing, borderpad=legend_borderpad
    )

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved as {output_file}")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot segment distribution over years as a line plot"
                    "saved as both a full-size PNG and a single-column PNG"
    )
    parser.add_argument("csv_file", help="Path to input segment distribution CSV file")
    parser.add_argument(
        "--full-output",
        default="segment_distribution_full.png",
        help="Output filename for the full-size plot (default: segment_distribution_full.png)"
    )
    parser.add_argument(
        "--column-output",
        default="segment_distribution_column.png",
        help="Output filename for the single-column plot (default: segment_distribution_column.png)"
    )
    args = parser.parse_args()

    # Full-size
    plot_segment_distribution(
        args.csv_file, args.full_output,
        figsize=FULL_FIGSIZE, label_fontsize=FULL_LABEL_FONTSIZE,
        tick_fontsize=FULL_TICK_FONTSIZE, legend_fontsize=FULL_LEGEND_FONTSIZE,
        linewidth=FULL_LINEWIDTH, markersize=FULL_MARKERSIZE,
        year_interval=1, legend_loc='upper left', legend_ncol=1
    )

    # Single-column
    plot_segment_distribution(
        args.csv_file, args.column_output,
        figsize=COLUMN_FIGSIZE, label_fontsize=COLUMN_LABEL_FONTSIZE,
        tick_fontsize=COLUMN_TICK_FONTSIZE, legend_fontsize=6,
        linewidth=COLUMN_LINEWIDTH, markersize=COLUMN_MARKERSIZE,
        year_interval=5, legend_loc='upper left', legend_ncol=1,
        legend_markerscale=0.9, legend_handlelength=1.4,
        legend_labelspacing=0.3, legend_borderpad=0.35
    )
