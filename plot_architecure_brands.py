#
# This script graphs architecture, CPU-brand, and GPU-brand trends for academic
# TOP500 systems over the lists 201111-202511, using the output of
# architecture_brands.py (architecture_brand_statistics.csv).
#
# It produces three figures (line plots, June-list year ticks):
#   - cpu_brand_trend.png         : count of systems per CPU brand over the years
#   - gpu_brand_trend.png         : count of systems per GPU/accelerator brand
#   - architecture_trend.png      : count of systems per architecture type
# and one combined stacked-area version of each if requested.
#
# To run: 'python3 plot_architecture_brands.py'
#

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Colorblind-friendly palette (Wong / Tol-style), reused across figures
PALETTE = [
    "#0173B2",  # blue
    "#DE8F05",  # orange
    "#029E73",  # green
    "#CC78BC",  # pink/purple
    "#CA9161",  # brown
    "#949494",  # grey
    "#ECE133",  # yellow
    "#56B4E9",  # sky blue
]


def load_data(csv_file="architecture_brand_statistics.csv",
              start=201111, end=202511):
    df = pd.read_csv(csv_file)
    df["Date"] = df["Date"].astype(int)
    df = df[(df["Date"] >= start) & (df["Date"] <= end)].copy()
    df = df.sort_values("Date").reset_index(drop=True)
    df["Year"] = df["Date"] // 100
    df["Month"] = df["Date"] % 100
    return df


def make_xticks(df):
    """Tick at each June list, labeled with the year; one label per year."""
    positions, labels, seen = [], [], set()
    for i, (_, row) in enumerate(df.iterrows()):
        if row["Month"] == 6 and row["Year"] not in seen:
            positions.append(i)
            labels.append(str(int(row["Year"])))
            seen.add(row["Year"])
    # If a year has only a November list (e.g. 201111), make sure it still shows
    for i, (_, row) in enumerate(df.iterrows()):
        if row["Year"] not in seen:
            positions.append(i)
            labels.append(str(int(row["Year"])))
            seen.add(row["Year"])
    order = np.argsort(positions)
    return list(np.array(positions)[order]), list(np.array(labels)[order])


def column_line_plot(df, columns, labels, ylabel, output_file,
                     drop_empty=True, year_step=2, legend_loc="upper left"):
    """Single-column version for a two-column paper.

    Sized natively at column width (~3.3in) with large fonts so that, once
    the figure is placed at \\columnwidth, the axis labels, ticks, and legend
    remain readable. `year_step` thins the x-axis to every Nth year so labels
    don't collide.
    """
    x = np.arange(len(df))
    # Column width ~3.3in; modest height keeps it from dominating the column.
    fig, ax = plt.subplots(figsize=(3.4, 2.6))

    ci = 0
    for col, label in zip(columns, labels):
        if col not in df.columns:
            continue
        y = df[col].values
        if drop_empty and np.nansum(y) == 0:
            continue
        ax.plot(x, y, label=label, color=PALETTE[ci % len(PALETTE)],
                linewidth=1.4, marker="o", markersize=2.5, alpha=0.9)
        ci += 1

    # Thin out x-ticks: keep every `year_step`-th June label
    positions, tick_labels = make_xticks(df)
    positions = list(positions)
    tick_labels = list(tick_labels)
    keep = list(range(0, len(positions), year_step))
    positions = [positions[i] for i in keep]
    tick_labels = [tick_labels[i] for i in keep]

    ax.set_xticks(positions)
    ax.set_xticklabels(tick_labels, rotation=0, fontsize=8)
    ax.tick_params(axis="y", labelsize=8)

    ax.set_xlabel("TOP500 List Year", fontsize=9, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=9, fontweight="bold")
    ax.grid(True, alpha=0.3, linestyle="--", axis="y", linewidth=0.6)
    ax.legend(loc=legend_loc, fontsize=8, framealpha=0.9,
              markerscale=1.6, handlelength=1.6, labelspacing=0.3,
              borderpad=0.4, ncol=1)
    # Headroom so the upper-left legend doesn't sit on top of the data
    ymax = max(np.nanmax(df[c].values) for c in columns if c in df.columns)
    ax.set_ylim(0, ymax * 1.15)

    plt.tight_layout(pad=0.3)
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"Saved {output_file}")
    plt.close(fig)


def line_plot(df, columns, labels, ylabel, output_file,
              title=None, drop_empty=True):
    """Generic multi-series line plot over the list index."""
    x = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(14, 8))

    ci = 0
    for col, label in zip(columns, labels):
        if col not in df.columns:
            continue
        y = df[col].values
        if drop_empty and np.nansum(y) == 0:
            continue  # skip categories that never appear
        ax.plot(x, y, label=label, color=PALETTE[ci % len(PALETTE)],
                linewidth=2.5, marker="o", markersize=5, alpha=0.9)
        ci += 1

    positions, tick_labels = make_xticks(df)
    ax.set_xticks(positions)
    ax.set_xticklabels(tick_labels, rotation=0)

    ax.set_xlabel("TOP500 List Year", fontsize=14, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=14, fontweight="bold")
    if title:
        ax.set_title(title, fontsize=15, fontweight="bold")
    ax.grid(True, alpha=0.3, linestyle="--", axis="y")
    ax.legend(loc="upper left", fontsize=13, framealpha=0.9,
              markerscale=1.3, ncol=1)
    ax.set_ylim(bottom=0)
    ax.tick_params(labelsize=12)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"Saved {output_file}")
    plt.close(fig)


def stacked_area_plot(df, columns, labels, ylabel, output_file,
                      title=None, drop_empty=True):
    """Stacked-area version, useful for showing composition over time."""
    x = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(14, 8))

    series, series_labels, colors = [], [], []
    ci = 0
    for col, label in zip(columns, labels):
        if col not in df.columns:
            continue
        y = np.nan_to_num(df[col].values, nan=0.0)
        if drop_empty and y.sum() == 0:
            continue
        series.append(y)
        series_labels.append(label)
        colors.append(PALETTE[ci % len(PALETTE)])
        ci += 1

    ax.stackplot(x, series, labels=series_labels, colors=colors, alpha=0.85)

    positions, tick_labels = make_xticks(df)
    ax.set_xticks(positions)
    ax.set_xticklabels(tick_labels, rotation=0)

    ax.set_xlabel("TOP500 List Year", fontsize=14, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=14, fontweight="bold")
    if title:
        ax.set_title(title, fontsize=15, fontweight="bold")
    ax.grid(True, alpha=0.3, linestyle="--", axis="y")
    ax.legend(loc="upper left", fontsize=13, framealpha=0.9, ncol=1)
    ax.set_ylim(bottom=0)
    ax.set_xlim(0, len(df) - 1)
    ax.tick_params(labelsize=12)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"Saved {output_file}")
    plt.close(fig)


def combined_cpu_gpu_plot(df, output_file="cpu_gpu_combined_trend.png"):
    """CPU brands (solid lines) and GPU brands (dashed lines) on one axis,
    distinguished by line style. Shared color per vendor where it makes sense
    so AMD/NVIDIA/Intel read consistently across the two families."""
    x = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(15, 9))

    # (column, label, color, linestyle, marker)
    cpu_series = [
        ("CPU_AMD",          "AMD (CPU)",          "#0173B2", "-", "o"),
        ("CPU_Intel",        "Intel (CPU)",        "#DE8F05", "-", "o"),
        ("CPU_IBM_Power",    "IBM Power (CPU)",    "#029E73", "-", "o"),
        ("CPU_NVIDIA_Grace", "NVIDIA Grace (CPU)", "#CC78BC", "-", "o"),
    ]
    gpu_series = [
        ("GPU_NVIDIA", "NVIDIA (GPU)", "#CC78BC", "--", "s"),
        ("GPU_AMD",    "AMD (GPU)",    "#0173B2", "--", "s"),
        ("GPU_Intel",  "Intel (GPU)",  "#DE8F05", "--", "s"),
    ]

    for col, label, color, ls, mk in cpu_series + gpu_series:
        if col not in df.columns:
            continue
        y = df[col].values
        if np.nansum(y) == 0:
            continue
        ax.plot(x, y, label=label, color=color, linestyle=ls,
                linewidth=2.5, marker=mk, markersize=5, alpha=0.9)

    positions, tick_labels = make_xticks(df)
    ax.set_xticks(positions)
    ax.set_xticklabels(tick_labels, rotation=0)

    ax.set_xlabel("TOP500 List Year", fontsize=14, fontweight="bold")
    ax.set_ylabel("Number of Systems", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, linestyle="--", axis="y")
    ax.set_ylim(bottom=0)
    ax.tick_params(labelsize=12)

    # Two-part legend: one for vendor/series, one explaining line style
    from matplotlib.lines import Line2D
    style_handles = [
        Line2D([0], [0], color="grey", linestyle="-", marker="o",
               linewidth=2.5, label="CPU (solid)"),
        Line2D([0], [0], color="grey", linestyle="--", marker="s",
               linewidth=2.5, label="GPU / accelerator (dashed)"),
    ]
    leg1 = ax.legend(loc="upper left", fontsize=12, framealpha=0.9,
                     markerscale=1.3, ncol=1)
    ax.add_artist(leg1)
    ax.legend(handles=style_handles, loc="upper center", fontsize=12,
              framealpha=0.9)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"Saved {output_file}")
    plt.close(fig)


def main():
    df = load_data()
    print(f"Loaded {len(df)} lists, {int(df['Date'].min())}-{int(df['Date'].max())}")

    # --- CPU brands ---
    cpu_cols = ["CPU_AMD", "CPU_Intel", "CPU_IBM_Power", "CPU_NVIDIA_Grace",
                "CPU_Other", "CPU_Unknown"]
    cpu_labels = ["AMD", "Intel", "IBM", "NVIDIA",
                  "Other", "Unknown"]
    line_plot(df, cpu_cols, cpu_labels,
              "Number of Systems", "cpu_brand_trend.png")
    stacked_area_plot(df, cpu_cols, cpu_labels,
                      "Number of Systems", "cpu_brand_stacked.png")

    # --- GPU / accelerator brands ---
    gpu_cols = ["GPU_NVIDIA", "GPU_AMD", "GPU_Intel", "GPU_Other"]
    gpu_labels = ["NVIDIA", "AMD", "Intel", "Other"]
    line_plot(df, gpu_cols, gpu_labels,
              "Number of Accelerated Systems", "gpu_brand_trend.png")
    stacked_area_plot(df, gpu_cols, gpu_labels,
                      "Number of Accelerated Systems", "gpu_brand_stacked.png")

    # --- Architecture ---
    arch_cols = ["Arch_MPP", "Arch_Cluster", "Arch_Constellation",
                 "Arch_SMP", "Arch_Other", "Arch_Unknown"]
    arch_labels = ["MPP", "Cluster", "Constellation", "SMP", "Other", "Unknown"]
    line_plot(df, arch_cols, arch_labels,
              "Number of Systems", "architecture_trend.png")
    stacked_area_plot(df, arch_cols, arch_labels,
                      "Number of Systems", "architecture_stacked.png")

    # --- Column-width versions for a single column of a two-column paper ---
    column_line_plot(df, cpu_cols, cpu_labels,
                     "Number of Systems", "cpu_brand_trend_column.png",
                     legend_loc="upper right")
    column_line_plot(df, gpu_cols, gpu_labels,
                     "Accelerated Systems", "gpu_brand_trend_column.png")


if __name__ == "__main__":
    main()
