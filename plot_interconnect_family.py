#
# This script plots interconnect family counts over time using line plot.
# It also outputs a stacked plot, a percentage distribution plot, and a
# single-column version sized for a two-column paper.
#
# To run script 'python3 plot_interconnect_family.py'
#

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

CSV_FILE = 'interconnect_family_counts_201006_to_202511-modified.csv'

# Colorblind-friendly palette (Okabe-Ito)
COLOR_MAP = {
    'Infiniband': '#0173B2',       # Blue
    'Gigabit Ethernet': '#DE8F05', # Orange
    'Omnipath': '#029E73',         # Green
    'Other': '#CC78BC',            # Purple
}
PALETTE = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC']


def plot_interconnect_families(csv_file=CSV_FILE):
    df = pd.read_csv(csv_file)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')

    plt.figure(figsize=(14, 8))
    interconnect_columns = [col for col in df.columns if col != 'Date']
    for column in interconnect_columns:
        color = COLOR_MAP.get(column, '#000000')
        plt.plot(df['Date'], df[column], marker='o', linewidth=2.5,
                 markersize=6, label=column, color=color, alpha=0.9)

    plt.xlabel('TOP500 List Year', fontsize=14, fontweight='bold')
    plt.ylabel('Count', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    plt.gcf().autofmt_xdate()
    plt.legend(loc='best', fontsize=12, framealpha=0.9)
    plt.tight_layout()
    plt.savefig('interconnect_family_plot.png', dpi=300, bbox_inches='tight')
    print("Plot saved to: interconnect_family_plot.png")
    plt.close()


def plot_stacked_area(csv_file=CSV_FILE):
    df = pd.read_csv(csv_file)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')

    plt.figure(figsize=(14, 8))
    interconnect_columns = [col for col in df.columns if col != 'Date']
    plt.stackplot(df['Date'], [df[col] for col in interconnect_columns],
                  labels=interconnect_columns, colors=PALETTE, alpha=0.8)

    plt.xlabel('TOP500 List Year', fontsize=14, fontweight='bold')
    plt.ylabel('Count', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')
    plt.gcf().autofmt_xdate()
    plt.legend(loc='upper left', fontsize=12, framealpha=0.9)
    plt.tight_layout()
    plt.savefig('interconnect_family_stacked_plot.png', dpi=300, bbox_inches='tight')
    print("Stacked plot saved to: interconnect_family_stacked_plot.png")
    plt.close()


def plot_percentage_distribution(csv_file=CSV_FILE):
    df = pd.read_csv(csv_file)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')

    interconnect_columns = [col for col in df.columns if col != 'Date']
    df_pct = df.copy()
    total = df[interconnect_columns].sum(axis=1)
    for col in interconnect_columns:
        df_pct[col] = (df[col] / total) * 100

    plt.figure(figsize=(14, 8))
    plt.stackplot(df_pct['Date'], [df_pct[col] for col in interconnect_columns],
                  labels=interconnect_columns, colors=PALETTE, alpha=0.8)

    plt.xlabel('TOP500 List Year', fontsize=14, fontweight='bold')
    plt.ylabel('Percentage (%)', fontsize=14, fontweight='bold')
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')
    plt.gcf().autofmt_xdate()
    plt.legend(loc='upper left', fontsize=12, framealpha=0.9)
    plt.tight_layout()
    plt.savefig('interconnect_family_percentage_plot.png', dpi=300, bbox_inches='tight')
    print("Percentage plot saved to: interconnect_family_percentage_plot.png")
    plt.close()


def plot_column_width(csv_file=CSV_FILE, year_step=2, legend_loc='upper left',
                      output_file='interconnect_family_column.png'):
    """Single-column version for a two-column paper.

    Rendered natively at ~column width (3.4in) with large proportional fonts so
    axis labels, ticks, and legend stay readable when placed at \\columnwidth.
    Uses explicit June-year ticks (thinned by `year_step`) rather than
    autofmt_xdate, which over-labels and rotates at small sizes.
    """
    df = pd.read_csv(csv_file)
    # Keep raw YYYYMM so we can build clean year ticks; also a datetime for x
    raw_dates = df['Date'].astype(int).tolist()
    x = np.arange(len(df))

    interconnect_columns = [col for col in df.columns if col != 'Date']

    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    for column in interconnect_columns:
        color = COLOR_MAP.get(column, '#000000')
        ax.plot(x, df[column].values, marker='o', linewidth=1.4,
                markersize=2.5, label=column, color=color, alpha=0.9)

    # Build x-ticks: one label per year at the June list, thinned by year_step
    positions, labels, seen = [], [], set()
    for i, d in enumerate(raw_dates):
        y, m = d // 100, d % 100
        if m == 6 and y not in seen:
            positions.append(i)
            labels.append(str(y))
            seen.add(y)
    keep = list(range(0, len(positions), year_step))
    positions = [positions[i] for i in keep]
    labels = [labels[i] for i in keep]

    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=0, fontsize=8)
    ax.tick_params(axis='y', labelsize=8)

    ax.set_xlabel('TOP500 List Year', fontsize=9, fontweight='bold')
    ax.set_ylabel('Count', fontsize=9, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--', axis='y', linewidth=0.6)
    ax.legend(loc=legend_loc, fontsize=8, framealpha=0.9, markerscale=1.6,
              handlelength=1.6, labelspacing=0.3, borderpad=0.4, ncol=1)

    # Headroom so the legend clears the data
    ymax = max(df[c].max() for c in interconnect_columns)
    ax.set_ylim(0, ymax * 1.15)

    plt.tight_layout(pad=0.3)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Column-width plot saved to: {output_file}")
    plt.close(fig)


if __name__ == "__main__":
    plot_interconnect_families(CSV_FILE)
    plot_stacked_area(CSV_FILE)
    plot_percentage_distribution(CSV_FILE)
    plot_column_width(CSV_FILE)
