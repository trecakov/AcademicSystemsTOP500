#
# This script extracts system perfomance statistics from AllListsAcademia directory and outputs the csv file.
# The system perfmance is calculated Rmax/Rpeak.
#
# It outputs quantiles, mean, meadian, highest and lowest system perfomance, and the top academic systems performance.
#
# To run script 'python3.6 performance_development-quantiles.py'
#


import pandas as pd
import os
import glob
import re
import numpy as np

def calculate_system_performance(input_dir="AllListsAcademia", output_file="system_performance_statistics.csv"):
    
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
                print(f"  Warning: 'Rmax' column not found in {filename}, skipping...")
                continue
            
            # Find Rpeak column
            rpeak_column = None
            possible_rpeak_names = ['Rpeak', 'RPeak', 'Rpeak [TFlop/s]', 'RPeak [TFlop/s]']
            
            for col_name in possible_rpeak_names:
                if col_name in df.columns:
                    rpeak_column = col_name
                    break
            
            # If exact match not found, try case-insensitive search
            if rpeak_column is None:
                for col in df.columns:
                    if 'rpeak' in col.lower():
                        rpeak_column = col
                        break
            
            if rpeak_column is None:
                print(f"  Warning: 'Rpeak' column not found in {filename}, skipping...")
                continue
            
            
            # Convert to numeric
            df['Rmax_numeric'] = pd.to_numeric(df[rmax_column], errors='coerce')
            df['Rpeak_numeric'] = pd.to_numeric(df[rpeak_column], errors='coerce')
            
            # Remove rows with NaN in either column
            df_clean = df[(df['Rmax_numeric'].notna()) & (df['Rpeak_numeric'].notna())].copy()
            
            # Remove rows where Rmax or Rpeak is 0 to avoid division issues
            df_clean = df_clean[(df_clean['Rmax_numeric'] > 0) & (df_clean['Rpeak_numeric'] > 0)].copy()
            
            if len(df_clean) == 0:
                print(f"  Warning: No valid Rmax/Rpeak pairs in {filename}, skipping...")
                continue
            
            # Calculate system performance (Rmax/Rpeak)
            # Higher ratio means more efficient (achieving more of peak performance)
            df_clean['Performance_Ratio'] = df_clean['Rmax_numeric'] / df_clean['Rpeak_numeric']
            
            performance_values = df_clean['Performance_Ratio']
            
            # Find the #1 system (highest Rmax) and its performance ratio
            max_rmax_idx = df_clean['Rmax_numeric'].idxmax()
            top_system_performance = df_clean.loc[max_rmax_idx, 'Performance_Ratio']
            
            # Calculate statistics and quantiles
            best = performance_values.max()  # Higher ratio is better (more efficient)
            worst = performance_values.min()  # Lower ratio is worse (less efficient)
            mean_perf = performance_values.mean()
            median_perf = performance_values.median()
            
            # Calculate quantiles
            q25 = performance_values.quantile(0.25)
            q50 = performance_values.quantile(0.50)  # Same as median
            q75 = performance_values.quantile(0.75)
            
            count = len(performance_values)
            
            results.append({
                'List': list_id,
                'Date': date_code,
                'Count': count,
                'Best': best,           # Maximum ratio (most efficient)
                'Q25': q25,
                'Median': median_perf,
                'Q75': q75,
                'Worst': worst,         # Minimum ratio (least efficient)
                'Mean': mean_perf,
                'Top_System_Performance': top_system_performance  # Performance of #1 system by Rmax
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
    df = calculate_system_performance()
