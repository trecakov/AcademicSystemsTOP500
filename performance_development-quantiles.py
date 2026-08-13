#
# This script extracts perfomance development statistics from TOP500Academic/ directory and outputs the csv file.
# The csv file has quantiles, mean, meadian, best, worst, sum of perfomance, and the top academic systems performance.
#
# To run script 'python3.6 performance_development-quantiles.py <lists directory> -o <output filename>'
#

import argparse
import pandas as pd
import os
import glob
import re

def process_rmax_values(input_dir, output_file="rmax_statistics.csv"):
    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))

    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return

    print(f"Found {len(csv_files)} CSV files")

    results = []

    # Process each CSV file
    for csv_file in sorted(csv_files):
        try:
            # Extract date/list identifier from filename
            filename = os.path.basename(csv_file)
            list_id = os.path.splitext(filename)[0]

            date_match = re.search(r'(\d{6})', list_id)
            date_code = date_match.group(1) if date_match else None

            print(f"\nProcessing {filename} (date code: {date_code})")

            # Read CSV file
            df = pd.read_csv(csv_file)

            # Find Rmax column
            rmax_column = None
            possible_names = ['Rmax', 'RMax', 'Rmax [TFlop/s]', 'RMax [TFlop/s]']

            for col_name in possible_names:
                if col_name in df.columns:
                    rmax_column = col_name
                    break

            # If match not found, do case-insensitive
            if rmax_column is None:
                for col in df.columns:
                    if 'rmax' in col.lower():
                        rmax_column = col
                        break

            if rmax_column is None:
                print(f"Warning: 'Rmax' column not found in {filename}, skipping...")
                print(f"  Available columns: {', '.join(df.columns)}")
                continue

            print(f"  Using column: '{rmax_column}'")

            # Convert Rmax to numeric
            df['Rmax_numeric'] = pd.to_numeric(df[rmax_column], errors='coerce')

            # Remove NaN values
            df_clean = df[df['Rmax_numeric'].notna()].copy()

            if len(df_clean) == 0:
                print(f"Warning: No valid Rmax values in {filename}, skipping...")
                continue

            # Convert GFlops/s to TFlops/s for lists from 199306 to 201611
            conversion_applied = False
            if date_code and len(date_code) == 6:
                date_int = int(date_code)
                if 199306 <= date_int <= 201611:
                    df_clean['Rmax_numeric'] = df_clean['Rmax_numeric'] / 1000.0
                    conversion_applied = True
                    print(f"  Converting GFlops/s to TFlops/s (date: {date_code})")

            rmax_values = df_clean['Rmax_numeric']

            # Compute statistics
            best = rmax_values.max()
            worst = rmax_values.min()
            total_sum = rmax_values.sum()
            count = len(rmax_values)

            # Calculate quantiles
            q25 = rmax_values.quantile(0.25)
            q50 = rmax_values.quantile(0.50)  # Median
            q75 = rmax_values.quantile(0.75)
            mean_val = rmax_values.mean()

            results.append({
                'List': list_id,
                'Best': best,
                'Worst': worst,
                'Sum': total_sum,
                'Count': count,
                'Q25': q25,
                'Median': q50,
                'Q75': q75,
                'Mean': mean_val
            })

            print(f"Processed {filename}: Best={best:.2f}, Worst={worst:.2f}, Sum={total_sum:.2f}, Median={q50:.2f}, Conversion={conversion_applied}")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

    # Create Dataframe
    results_df = pd.DataFrame(results)

    # Save to CSV
    results_df.to_csv(output_file, index=False)
    print(f"\nResults saved to {output_file}")
    print(f"Total lists processed: {len(results)}")

    return results_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract Rmax performance development statistics"
    )
    parser.add_argument("input_dir", help="Path to directory containing CSV files")
    parser.add_argument(
        "-o", "--output",
        default="rmax_statistics.csv",
        help="Path to output CSV file (default: rmax_statistics.csv)"
    )
    args = parser.parse_args()

    df = process_rmax_values(args.input_dir, args.output)
    if df is not None:
        print("\nSummary:")
        print(df.head())
