#
# This script extracts energy efficiency statistics from input directory and outputs 06/2008-06/2026 the csv file.
# The file has quantiles, mean, meadian, highest, lowest and top systems energy efficiency points. 
#
# To run script 'python3.6 energy_efficiency.py <lists directory> -o <output file name>'
#

import argparse
import pandas as pd
import os
import glob
import re
import numpy as np

def calculate_energy_efficiency_quantiles(input_dir, output_file="energy_efficiency_quantiles.csv",
                                            min_date_code=200806, max_date_code=202606):
    
    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    # Filter files from 200806 to 202606
    filtered_files = []
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        date_match = re.search(r'(\d{6})', filename)
        if date_match:
            date_code = int(date_match.group(1))
            if min_date_code <= date_code <= max_date_code:
                filtered_files.append(csv_file)
    
    if not filtered_files:
        print(f"No CSV files found in date range {min_date_code}-{max_date_code}")
        return
    
    print(f"Found {len(filtered_files)} CSV files in date range")
    
    results = []
    
    # Process each CSV
    for csv_file in sorted(filtered_files):
        try:
            filename = os.path.basename(csv_file)
            list_id = os.path.splitext(filename)[0]
            
            # Extract date code from filename
            date_match = re.search(r'(\d{6})', list_id)
            date_code = date_match.group(1) if date_match else None
            
            print(f"\nProcessing {filename} (date code: {date_code})")
            
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Find Rmax column
            rmax_column = None
            possible_rmax_names = ['Rmax', 'RMax', 'Rmax [TFlop/s]', 'RMax [TFlop/s]']
            
            for col_name in possible_rmax_names:
                if col_name in df.columns:
                    rmax_column = col_name
                    break
            
            # If exact match not found, do case-insensitive
            if rmax_column is None:
                for col in df.columns:
                    if 'rmax' in col.lower():
                        rmax_column = col
                        break
            
            if rmax_column is None:
                print(f"  Warning: 'Rmax' column not found, skipping...")
                continue
            
            # Find Power column
            power_column = None
            possible_power_names = ['Power', 'Power (kW)', 'Power [kW]']
            
            for col_name in possible_power_names:
                if col_name in df.columns:
                    power_column = col_name
                    break
            
            # If exact match not found, do case-insensitive
            if power_column is None:
                for col in df.columns:
                    if 'power' in col.lower():
                        power_column = col
                        break
            
            if power_column is None:
                print(f"  Warning: 'Power' column not found, skipping...")
                continue
            
            # Convert to numeric
            df['Rmax_numeric'] = pd.to_numeric(df[rmax_column], errors='coerce')
            df['Power_numeric'] = pd.to_numeric(df[power_column], errors='coerce')
            
            # Remove rows with NaN in either Rmax or Power
            df_clean = df[(df['Rmax_numeric'].notna()) & (df['Power_numeric'].notna())].copy()
            
            # Also remove rows where Power is 0 to avoid division by zero
            df_clean = df_clean[df_clean['Power_numeric'] > 0].copy()
            
            if len(df_clean) == 0:
                print(f"  Warning: No valid Rmax/Power pairs in {filename}, skipping...")
                continue
            
            # Convert GFlops/s to TFlops/s for files from 200806 to 201611
            conversion_applied = False
            if date_code:
                try:
                    date_int = int(date_code)
                    if 200806 <= date_int <= 201611:
                        df_clean['Rmax_numeric'] = df_clean['Rmax_numeric'] / 1000.0
                        conversion_applied = True
                        print(f"  Converting GFlops/s to TFlops/s")
                except:
                    pass
            
            # Calculate energy efficiency (TFlops/kW or GFlops/kW depending on conversion)
            df_clean['Energy_Efficiency'] = df_clean['Rmax_numeric'] / df_clean['Power_numeric']
            
            efficiency_values = df_clean['Energy_Efficiency']
            
            # Find the top system (highest Rmax) and its energy efficiency
            max_rmax_idx = df_clean['Rmax_numeric'].idxmax()
            top_system = df_clean.loc[max_rmax_idx]
            top_rmax = top_system['Rmax_numeric']
            top_power = top_system['Power_numeric']
            top_efficiency = top_system['Energy_Efficiency']
            
            # Calculate statistics and quantiles (without Q10 and Q90)
            mean_eff = efficiency_values.mean()
            median_eff = efficiency_values.median()
            min_eff = efficiency_values.min()
            max_eff = efficiency_values.max()
            
            # Calculate quantiles 
            q25 = efficiency_values.quantile(0.25)
            q50 = efficiency_values.quantile(0.50)  # Same as median
            q75 = efficiency_values.quantile(0.75)
            
            count = len(efficiency_values)
            
            results.append({
                'List': list_id,
                'Date': date_code,
                'Count': count,
                'Min_Efficiency': min_eff,
                'Q25': q25,
                'Median': median_eff,
                'Q75': q75,
                'Max_Efficiency': max_eff,
                'Mean_Efficiency': mean_eff,
                'Top_System_Rmax': top_rmax,
                'Top_System_Power': top_power,
                'Top_System_Efficiency': top_efficiency,
                'Conversion_Applied': conversion_applied
            })
            
        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")
            continue
    
    # Create Dataframe
    results_df = pd.DataFrame(results)
    
    # Save to CSV
    results_df.to_csv(output_file, index=False)
    
    return results_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract energy efficiency (Rmax/Power) statistics from lists directory"
    )
    parser.add_argument("input_dir", help="Path to directory containing CSV files")
    parser.add_argument(
        "-o", "--output",
        default="energy_efficiency_quantiles.csv",
        help="Path to output CSV file (default: energy_efficiency_quantiles.csv)"
    )
    parser.add_argument(
        "--min-date-code",
        type=int,
        default=200806,
        help="Only process lists with a date code (YYYYMM) at or after this value (default: 200806)"
    )
    parser.add_argument(
        "--max-date-code",
        type=int,
        default=202606,
        help="Only process lists with a date code (YYYYMM) at or before this value (default: 202606)"
    )
    args = parser.parse_args()

    df = calculate_energy_efficiency_quantiles(
        args.input_dir, args.output, args.min_date_code, args.max_date_code
    )
