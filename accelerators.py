#
# This script extracts accelerator statistics from a directory and outputs the csv file.
# We only output 2011-2026, both total core and accelerators core statistics such as 
# quantiles, mean, meadian, highest and lowest core count for both total core and accelerators
# core counts.  
#
# To run script 'python3.6 accelerators.py <lists directory> -o <output file name>'
#

import argparse
import pandas as pd
import os
import glob
import re
import numpy as np

def extract_accelerator_statistics(input_dir, output_file="accelerator_statistics.csv",
                                     min_year=2011, max_year=2026):
    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    # Filter files from 2011 to 2026
    filtered_files = []
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        date_match = re.search(r'(\d{6})', filename)
        if date_match:
            date_code = int(date_match.group(1))
            year = date_code // 100
            if min_year <= year <= max_year:
                filtered_files.append(csv_file)
    
    if not filtered_files:
        print(f"No CSV files found from {min_year}-{max_year} in {input_dir}")
        return
    
    print(f"Found {len(filtered_files)} CSV files from {min_year}-{max_year}")
    
    results = []
    
    # Process each CSVs
    for csv_file in sorted(filtered_files):
        try:
            filename = os.path.basename(csv_file)
            list_id = os.path.splitext(filename)[0]
            
            # Extract date code 
            date_match = re.search(r'(\d{6})', list_id)
            date_code = date_match.group(1) if date_match else None
            
            print(f"\nProcessing {filename} (date code: {date_code})")
            
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Find Accelerator/Co-Processor
            accelerator_column = None
            possible_names = ['Accelerator/Co-Processor', 'Accelerator/Co-processor', 
                            'Accelerator', 'Co-Processor', 'Coprocessor']
            
            for col_name in possible_names:
                if col_name in df.columns:
                    accelerator_column = col_name
                    break
            
            # Find Accelerator/Co-Processor Cores
            cores_column = None
            possible_cores_names = ['Accelerator/Co-Processor Cores', 'Accelerator/Co-processor Cores',
                                   'Accelerator Cores', 'Co-Processor Cores', 'Coprocessor Cores']
            
            for col_name in possible_cores_names:
                if col_name in df.columns:
                    cores_column = col_name
                    break
            
            # Find Total Cores
            total_cores_column = None
            possible_total_cores_names = ['Total Cores', 'Cores', 'Total cores', 'total cores']
            
            for col_name in possible_total_cores_names:
                if col_name in df.columns:
                    total_cores_column = col_name
                    break
            
            if cores_column is None:
                print(f"  Warning: 'Accelerator/Co-Processor Cores' column not found, skipping...")
                continue
            
            if total_cores_column is None:
                print(f"  Warning: 'Total Cores' column not found, skipping...")
                continue
            
            # Find Rmax to identify #1 system
            rmax_column = None
            possible_rmax_names = ['Rmax', 'RMax', 'Rmax [TFlop/s]', 'RMax [TFlop/s]']
            
            for col_name in possible_rmax_names:
                if col_name in df.columns:
                    rmax_column = col_name
                    break
            
            if rmax_column is None:
                for col in df.columns:
                    if 'rmax' in col.lower():
                        rmax_column = col
                        break
            
            
            # Count systems with accelerators (not "None")
            accelerator_count = df[accelerator_column].notna().sum()
            accelerator_count -= (df[accelerator_column] == 'None').sum()
            accelerator_count -= (df[accelerator_column].astype(str).str.strip() == '').sum()
            
            # Filter systems with accelerators
            has_accelerator = (df[accelerator_column].notna()) & \
                             (df[accelerator_column] != 'None') & \
                             (df[accelerator_column].astype(str).str.strip() != '')
            
            df_with_accel = df[has_accelerator].copy()
            
            # Convert cores to numeric
            df_with_accel['Cores_numeric'] = pd.to_numeric(df_with_accel[cores_column], errors='coerce')
            
            # Remove NaN and zero values
            accel_cores_values = df_with_accel['Cores_numeric'].dropna()
            accel_cores_values = accel_cores_values[accel_cores_values > 0]
            
            # Get total cores for all systems
            df['Total_Cores_numeric'] = pd.to_numeric(df[total_cores_column], errors='coerce')
            total_cores_values = df['Total_Cores_numeric'].dropna()
            total_cores_values = total_cores_values[total_cores_values > 0]
            
            # Find #1 system and get its info
            top_system_has_accel = False
            top_system_accel_cores = None
            top_system_total_cores = None
            
            if rmax_column is not None and len(df) > 0:
                df['Rmax_numeric'] = pd.to_numeric(df[rmax_column], errors='coerce')
                df_clean = df[df['Rmax_numeric'].notna()].copy()
                
                if len(df_clean) > 0:
                    max_rmax_idx = df_clean['Rmax_numeric'].idxmax()
                    top_system = df_clean.loc[max_rmax_idx]
                    
                    # Check accelerator
                    top_accel = top_system[accelerator_column]
                    if pd.notna(top_accel) and str(top_accel).strip() != '' and str(top_accel) != 'None':
                        top_system_has_accel = True
                        top_cores_value = top_system[cores_column]
                        if pd.notna(top_cores_value):
                            try:
                                top_system_accel_cores = float(top_cores_value)
                            except:
                                pass
                    
                    # Get total cores
                    top_total_cores_value = top_system[total_cores_column]
                    if pd.notna(top_total_cores_value):
                        try:
                            top_system_total_cores = float(top_total_cores_value)
                        except:
                            pass
            
            # Calculate statistics for accelerator cores
            if len(accel_cores_values) > 0:
                accel_best = accel_cores_values.min()
                accel_worst = accel_cores_values.max()
                accel_mean = accel_cores_values.mean()
                accel_median = accel_cores_values.median()
                
                accel_q25 = accel_cores_values.quantile(0.25)
                accel_q50 = accel_cores_values.quantile(0.50)
                accel_q75 = accel_cores_values.quantile(0.75)
            else:
                accel_best = accel_worst = accel_mean = accel_median = accel_q25 = accel_q50 = accel_q75 = None
            
            # Calculate statistics for total cores
            if len(total_cores_values) > 0:
                total_best = total_cores_values.min()
                total_worst = total_cores_values.max()
                total_mean = total_cores_values.mean()
                total_median = total_cores_values.median()
                
                total_q25 = total_cores_values.quantile(0.25)
                total_q50 = total_cores_values.quantile(0.50)
                total_q75 = total_cores_values.quantile(0.75)
            else:
                total_best = total_worst = total_mean = total_median = total_q25 = total_q50 = total_q75 = None
            
            results.append({
                'List': list_id,
                'Date': date_code,
                'Systems_With_Accelerators': accelerator_count,
                'Total_Systems': len(df),
                'Accel_Cores_Best': accel_best,
                'Accel_Cores_Q25': accel_q25,
                'Accel_Cores_Median': accel_median,
                'Accel_Cores_Q75': accel_q75,
                'Accel_Cores_Worst': accel_worst,
                'Accel_Cores_Mean': accel_mean,
                'Total_Cores_Best': total_best,
                'Total_Cores_Q25': total_q25,
                'Total_Cores_Median': total_median,
                'Total_Cores_Q75': total_q75,
                'Total_Cores_Worst': total_worst,
                'Total_Cores_Mean': total_mean,
                'Top_System_Has_Accelerator': top_system_has_accel,
                'Top_System_Accel_Cores': top_system_accel_cores,
                'Top_System_Total_Cores': top_system_total_cores
            })
            
            
        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    # Create Dataframe
    results_df = pd.DataFrame(results)
    
    # Save to CSV
    results_df.to_csv(output_file, index=False)
    
    return results_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract accelerator/co-processor core statistics from a directory"
    )
    parser.add_argument("input_dir", help="Path to directory containing CSV files")
    parser.add_argument(
        "-o", "--output",
        default="accelerator_statistics.csv",
        help="Path to output CSV file (default: accelerator_statistics.csv)"
    )
    parser.add_argument(
        "--min-year",
        type=int,
        default=2011,
        help="Only process lists from this year onwards (default: 2011)"
    )
    parser.add_argument(
        "--max-year",
        type=int,
        default=2026,
        help="Only process lists up to this year (default: 2026)"
    )
    args = parser.parse_args()

    df = extract_accelerator_statistics(args.input_dir, args.output, args.min_year, args.max_year)
