#
# This script extracts energy efficiency statistics from Top500_without_Academic directory and outputs the csv file.
# We only output 06/2008-11/2025 data since before that there was no Power data included in TOP500.
#
# It outputs quantiles, mean, meadian, highest, lowest and top systems energy efficiency points. 
# We had to do a power unit conversion from 2008/06 - 2016/11 since those lists used GFlop/s. 
# The energy efficiency = Rmax/Power.
#
# To run script 'python3.6 energy_efficiency.py'
#

import pandas as pd
import os
import glob
import re
import numpy as np

def calculate_energy_efficiency_quantiles(input_dir="Top500_without_Academic", output_file="energy_efficiency_quantiles_non_academic.csv"):
    
    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    # Filter files from 200806A to 202511A
    filtered_files = []
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        date_match = re.search(r'(\d{6})', filename)
        if date_match:
            date_code = int(date_match.group(1))
            if 200806 <= date_code <= 202511:
                filtered_files.append(csv_file)
    
    if not filtered_files:
        print(f"No CSV files found in date range 200806-202511")
        return
    
    print(f"Found {len(filtered_files)} CSV files in date range")
    
    results = []
    
    # Process each CSV file
    for csv_file in sorted(filtered_files):
        try:
            filename = os.path.basename(csv_file)
            list_id = os.path.splitext(filename)[0]
            
            # Extract date code from filename
            date_match = re.search(r'(\d{6})', list_id)
            date_code = date_match.group(1) if date_match else None
            
            print(f"\nProcessing {filename} (date code: {date_code})")
            
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Find Rmax column
            rmax_column = None
            possible_rmax_names = ['Rmax', 'RMax', 'Rmax [TFlop/s]', 'RMax [TFlop/s]']
            
            for col_name in possible_rmax_names:
                if col_name in df.columns:
                    rmax_column = col_name
                    break
            
            # If exact match not found, try case-insensitive search
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
            
            # If exact match not found, try case-insensitive search
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
            
            # Calculate quantiles (25th, 50th, 75th percentiles only)
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
    
    # Create DataFrame from results
    results_df = pd.DataFrame(results)
    
    # Save to CSV
    results_df.to_csv(output_file, index=False)
    
    return results_df

if __name__ == "__main__":
    df = calculate_energy_efficiency_quantiles()
