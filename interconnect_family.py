#
# This script extracts interconnect family statistics from a directory and outputs the csv with counts per year from 06/2010-06/2026.
#
# To run script 'python3.6 interconnect_family.py'
#

import argparse
import os
import pandas as pd
from pathlib import Path
import re

def load_with_detected_header(file_path, ext):
    
    # Read without header
    if ext == ".csv":
        temp_df = pd.read_csv(file_path, header=None)
    elif ext == ".xlsx":
        temp_df = pd.read_excel(file_path, header=None, engine="openpyxl")
    elif ext == ".xls":
        temp_df = pd.read_excel(file_path, header=None, engine="xlrd")
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    # Detect header row
    header_row = 0
    for idx in range(min(5, len(temp_df))):  # Check first 5 rows
        row = temp_df.iloc[idx]
        non_numeric = sum(isinstance(val, str) for val in row)
        if non_numeric > len(row) * 0.5:  # If more than 50% are strings
            header_row = idx
            break
    
    # Reload with header
    if ext == ".csv":
        df = pd.read_csv(file_path, header=header_row)
    elif ext == ".xlsx":
        df = pd.read_excel(file_path, header=header_row, engine="openpyxl")
    elif ext == ".xls":
        df = pd.read_excel(file_path, header=header_row, engine="xlrd")
    
    return df


def extract_date_from_filename(filename):
    
    # Look for pattern
    match = re.search(r'(\d{6})', filename)
    if match:
        return match.group(1)
    return None


def count_interconnect_families(root_directory, start_date='201006', end_date='202606', column_name='Interconnect Family'):
    
    # Convert to Path object
    root_path = Path(root_directory)
    
    # Check if directory exists
    if not root_path.exists():
        print(f"Error: Directory '{root_directory}' does not exist")
        return pd.DataFrame()
    
    # Supported file extensions
    supported_extensions = ['.csv', '.xlsx', '.xls']
    
    # Dictionary to store counts: {date: {interconnect_family: count}}
    data_by_date = {}
    files_processed = 0
    files_skipped = 0
    
    # Check files
    for file_path in sorted(root_path.rglob('*')):
        ext = file_path.suffix.lower()
        
        if ext not in supported_extensions:
            continue
        
        # Extract date from filename
        file_date = extract_date_from_filename(file_path.name)
        
        if not file_date:
            print(f"No date found in filename: {file_path.name}")
            files_skipped += 1
            continue
        
        # Check if date is within range
        if file_date < start_date or file_date > end_date:
            files_skipped += 1
            continue
        
        try:
            # Load file with header detection
            df = load_with_detected_header(file_path, ext)
            
            # Check if column exists
            if column_name not in df.columns:
                files_skipped += 1
                continue
            
            # Count occurrences of each value in the column
            counts = df[column_name].value_counts().to_dict()
            
            # Store in data structure
            if file_date not in data_by_date:
                data_by_date[file_date] = {}
            
            data_by_date[file_date] = counts
            files_processed += 1
            
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {str(e)}")
            files_skipped += 1
    
    if not data_by_date:
        print("No data collected!")
        return pd.DataFrame()
    
    # Convert to Dataframe
    all_values = set()
    for counts in data_by_date.values():
        all_values.update(counts.keys())
    
    # Remove NaN 
    all_values = {v for v in all_values if pd.notna(v)}
    
    # Create Dataframe 
    result_data = []
    for date in sorted(data_by_date.keys()):
        row = {'Date': date}
        for value in sorted(all_values):
            row[value] = data_by_date[date].get(value, 0)
        result_data.append(row)
    
    result_df = pd.DataFrame(result_data)
    
    return result_df


def explore_file_structure(root_directory):
    
    root_path = Path(root_directory)
    supported_extensions = ['.csv', '.xlsx', '.xls']
    
    for file_path in root_path.rglob('*'):
        ext = file_path.suffix.lower()
        
        if ext not in supported_extensions:
            continue
        
        try:
            df = load_with_detected_header(file_path, ext)
            
            # Check for date in filename
            file_date = extract_date_from_filename(file_path.name)
            return df.columns.tolist()
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            continue
    
    return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract interconnect family counts per list from a directory"
    )
    parser.add_argument("input_dir", help="Path to directory containing TOP500 list files (CSV/XLSX/XLS)")
    parser.add_argument(
        "--start-date",
        default="201006",
        help="Only process lists with a date code (YYYYMM) at or after this value (default: 201006)"
    )
    parser.add_argument(
        "--end-date",
        default="202606",
        help="Only process lists with a date code (YYYYMM) at or before this value (default: 202606)"
    )
    parser.add_argument(
        "--column",
        default="Interconnect Family",
        help="Name of the column to count values from (default: 'Interconnect Family')"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Path to output CSV file (default: <column>_counts_<start>_to_<end>.csv)"
    )
    args = parser.parse_args()

    root_dir = args.input_dir
    start_date = args.start_date
    end_date = args.end_date
    column_choice = args.column

    columns = explore_file_structure(root_dir)

    # Get counts
    result_df = count_interconnect_families(root_dir, start_date, end_date, column_choice)

    # Save to CSV
    if args.output:
        output_file = args.output
    else:
        safe_column_name = column_choice.lower().replace(' ', '_').replace('/', '_')
        output_file = f"{safe_column_name}_counts_{start_date}_to_{end_date}.csv"
    result_df.to_csv(output_file, index=False)
    print(f"Saved results to {output_file}")
