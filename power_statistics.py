#
# This script extracts the power statistics form AllListsAcademia directory from 06/2008 and outputs the csv file.
# The output contains count of power enties per list, quantiles, mean, median, and top academic systems power consumption. 
#
# To run script 'python3.6 power_statistics.py'
#

import pandas as pd
import os
import glob
import re
import numpy as np

def extract_power_statistics(input_dir="AllListsAcademia", output_file="power_statistics.csv"):
    
    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    # Filter files from 200806 onwards
    filtered_files = []
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        date_match = re.search(r'(\d{6})', filename)
        if date_match:
            date_code = int(date_match.group(1))
            if date_code >= 200806:
                filtered_files.append(csv_file)
    
    if not filtered_files:
        print(f"No CSV files found from 200806 onwards in {input_dir}")
        return
    
    
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
                    if 'power' in col.lower() and 'kw' in col.lower():
                        power_column = col
                        break
            
            # If still not found, try just 'power'
            if power_column is None:
                for col in df.columns:
                    if col.lower() == 'power':
                        power_column = col
                        break
            
            if power_column is None:
                print(f"  Warning: 'Power' column not found in {filename}, skipping...")
                print(f"  Available columns: {', '.join(df.columns[:10])}...")
                continue
            
            # Find Rmax column to identify #1 system
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
            
            # Convert Power to numeric
            df['Power_numeric'] = pd.to_numeric(df[power_column], errors='coerce')
            
            # Remove rows with NaN or zero power values
            power_values = df['Power_numeric'].dropna()
            power_values = power_values[power_values > 0]
            
            if len(power_values) == 0:
                print(f"  Warning: No valid Power values in {filename}, skipping...")
                continue
            
            # Find #1 system (highest Rmax) and its power consumption
            top_system_power = None
            if rmax_column is not None:
                df['Rmax_numeric'] = pd.to_numeric(df[rmax_column], errors='coerce')
                df_clean = df[(df['Power_numeric'].notna()) & (df['Power_numeric'] > 0) & 
                             (df['Rmax_numeric'].notna())].copy()
                
                if len(df_clean) > 0:
                    max_rmax_idx = df_clean['Rmax_numeric'].idxmax()
                    top_system_power = df_clean.loc[max_rmax_idx, 'Power_numeric']
                else:
                    print(f"  Warning: Could not determine #1 system")
            else:
                print(f"  Warning: Rmax column not found, cannot identify #1 system")
            
            # Calculate statistics and quantiles
            lowest = power_values.min()  # Minimum power (most efficient)
            highest = power_values.max()  # Maximum power (least efficient)
            mean_power = power_values.mean()
            median_power = power_values.median()
            
            # Calculate quantiles
            q25 = power_values.quantile(0.25)
            q50 = power_values.quantile(0.50)  # Same as median
            q75 = power_values.quantile(0.75)
            
            count = len(power_values)
            
            results.append({
                'List': list_id,
                'Date': date_code,
                'Count': count,
                'Lowest': lowest,   
                'Q25': q25,
                'Median': median_power,
                'Q75': q75,
                'Highest': highest,
                'Mean': mean_power,
                'Top_System_Power': top_system_power  # Power of #1 system
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
    df = extract_power_statistics()
