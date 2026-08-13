#
# This script extracts the top academic system from each list from a list directory and outputs the csv file.
#
# To run script 'python3.6 top_academic_systems_over_years.py'
#


import argparse
import pandas as pd
import os
import glob
import re

def extract_top_systems(input_dir, output_file="top_academic_systems.csv"):
    
    # Get all CSVs
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV files")
    
    results = []
    
    # Process each CSV
    for csv_file in sorted(csv_files):
        try:
            filename = os.path.basename(csv_file)
            list_id = os.path.splitext(filename)[0]
            
            # Extract date code from filename
            date_match = re.search(r'(\d{6})', list_id)
            date_code = date_match.group(1) if date_match else None
            
            print(f"\nProcessing {filename} (date code: {date_code})")
            
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Find Rmax
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
                print(f"  Warning: 'Rmax' column not found in {filename}, skipping...")
                print(f"  Available columns: {', '.join(df.columns[:10])}...")
                continue
            
            # Convert Rmax to numeric
            df['Rmax_numeric'] = pd.to_numeric(df[rmax_column], errors='coerce')
            
            # Remove rows with NaN Rmax
            df_clean = df[df['Rmax_numeric'].notna()].copy()
            
            if len(df_clean) == 0:
                print(f"  Warning: No valid Rmax values in {filename}, skipping...")
                continue
            
            # Find the top system (highest Rmax)
            max_rmax_idx = df_clean['Rmax_numeric'].idxmax()
            top_system = df_clean.loc[max_rmax_idx]
            
            # Create result dictionary
            result = {
                'List': list_id,
                'Date': date_code,
            }
            
            # Add ALL columns from the original CSV for the top system
            for col in df.columns:
                result[col] = top_system[col]
            
            # Add the numeric Rmax value we calculated
            result['Rmax_Numeric'] = top_system['Rmax_numeric']
            
            results.append(result)
            
        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")
            continue
    
    # Create Dataframe
    results_df = pd.DataFrame(results)
    
    # Reorder columns
    metadata_cols = ['List', 'Date']
    other_cols = [col for col in results_df.columns if col not in metadata_cols]
    results_df = results_df[metadata_cols + other_cols]
    
    # Save to CSV
    results_df.to_csv(output_file, index=False)
    
    return results_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract the top academic system from each list in a directory"
    )
    parser.add_argument("input_dir", help="Path to directory containing CSV files")
    parser.add_argument(
        "-o", "--output",
        default="top_systems.csv",
        help="Path to output CSV file (default: top_academic_systems.csv)"
    )
    args = parser.parse_args()

    df = extract_top_systems(args.input_dir, args.output)
