#
# This script extracts age statistics from AllListsAcademia directory and outputs the csv file over the years.
#
# It outputs quantiles, mean, meadian, highest and lowest age, and top systems.
#
# To run script 'python3.6 analyze_age.py'
#

import pandas as pd
import os
import glob
import re
import numpy as np

def analyze_year_field(input_dir="AllListsAcademia", output_file="year_field_statistics.csv"):
    
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
            
            # Find Year column
            year_column = None
            possible_year_names = ['Year', 'year', 'YEAR', 'Year of Installation']
            
            for col_name in possible_year_names:
                if col_name in df.columns:
                    year_column = col_name
                    break
            
            # If exact match not found, try case-insensitive search
            if year_column is None:
                for col in df.columns:
                    if 'year' in col.lower():
                        year_column = col
                        break
            
            if year_column is None:
                print(f"  Warning: 'Year' column not found, skipping...")
                print(f"  Available columns: {', '.join(df.columns[:10])}...")
                continue
            
            print(f"  Using Year column: '{year_column}'")
            
            # Find Rmax column to identify top system
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
                print(f"  Warning: 'Rmax' column not found, cannot identify top system")
                top_system_year = None
            else:
                print(f"  Using Rmax column: '{rmax_column}'")
                # Convert Rmax to numeric
                df['Rmax_numeric'] = pd.to_numeric(df[rmax_column], errors='coerce')
            
            # Convert Year to numeric
            df['Year_numeric'] = pd.to_numeric(df[year_column], errors='coerce')
            
            # Remove NaN values
            year_values = df['Year_numeric'].dropna()
            
            if len(year_values) == 0:
                print(f"  Warning: No valid Year values in {filename}, skipping...")
                continue
            
            # Find the top system (highest Rmax) and its year
            if rmax_column is not None and 'Rmax_numeric' in df.columns:
                df_clean = df[(df['Year_numeric'].notna()) & (df['Rmax_numeric'].notna())].copy()
                if len(df_clean) > 0:
                    max_rmax_idx = df_clean['Rmax_numeric'].idxmax()
                    top_system = df_clean.loc[max_rmax_idx]
                    top_system_year = int(top_system['Year_numeric']) if pd.notna(top_system['Year_numeric']) else None
                    top_system_rmax = top_system['Rmax_numeric']
                else:
                    top_system_year = None
                    top_system_rmax = None
            else:
                top_system_year = None
                top_system_rmax = None
            
            # Calculate statistics and quantiles
            oldest = year_values.min()
            newest = year_values.max()
            mean_year = year_values.mean()
            median_year = year_values.median()
            
            # Calculate quantiles
            q25 = year_values.quantile(0.25)
            q50 = year_values.quantile(0.50)  # Same as median
            q75 = year_values.quantile(0.75)
            
            count = len(year_values)
            
            results.append({
                'List': list_id,
                'Date': date_code,
                'Count': count,
                'Oldest': int(oldest),
                'Q25': q25,
                'Median': median_year,
                'Q75': q75,
                'Newest': int(newest),
                'Mean': mean_year,
                'Top_System_Year': top_system_year,
                'Top_System_Rmax': top_system_rmax
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
    df = analyze_year_field()
