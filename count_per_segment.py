#
# This script extracts segment statistics from AllLists directory(TOP500 lists) across years and outputs the csv file.
#
# To run script 'python3.6 count_per_segment.py'
#


import pandas as pd
import os
import glob
import re

def load_with_detected_header(file_path, ext):
    """Load file with automatic header detection."""
    # Read without header first
    if ext == ".csv":
        temp_df = pd.read_csv(file_path, header=None)
    elif ext == ".xlsx":
        temp_df = pd.read_excel(file_path, header=None, engine="openpyxl")
    elif ext == ".xls":
        temp_df = pd.read_excel(file_path, header=None, engine="xlrd")
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    # Detect header row (look for common column names in first few rows)
    header_keywords = ['rank', 'site', 'system', 'cores', 'rmax', 'country', 'segment']
    header_row = 0
    
    for i in range(min(10, len(temp_df))):
        row_text = ' '.join([str(val).lower() for val in temp_df.iloc[i] if pd.notna(val)])
        if any(keyword in row_text for keyword in header_keywords):
            header_row = i
            break
    
    # Read again with detected header
    if ext == ".csv":
        df = pd.read_csv(file_path, header=header_row)
    elif ext == ".xlsx":
        df = pd.read_excel(file_path, header=header_row, engine="openpyxl")
    elif ext == ".xls":
        df = pd.read_excel(file_path, header=header_row, engine="xlrd")
    
    return df

def extract_segment_distribution(input_dir="AllLists", output_file="segment_distribution.csv"):
    
    # Get all CSV and Excel files in the directory
    file_patterns = [
        os.path.join(input_dir, "*.csv"),
        os.path.join(input_dir, "*.xlsx"),
        os.path.join(input_dir, "*.xls")
    ]
    
    all_files = []
    for pattern in file_patterns:
        all_files.extend(glob.glob(pattern))
    
    if not all_files:
        print(f"No CSV or Excel files found in {input_dir}")
        return
    
    print(f"Found {len(all_files)} files")
    
    results = []
    
    # Process each file
    for file_path in sorted(all_files):
        try:
            filename = os.path.basename(file_path)
            list_id = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1].lower()
            
            # Extract date code from filename
            date_match = re.search(r'(\d{6})', list_id)
            date_code = date_match.group(1) if date_match else None
            
            print(f"\nProcessing {filename} (date code: {date_code})")
            
            # Read file with header detection
            df = load_with_detected_header(file_path, ext)
            
            # Find Segment column
            segment_column = None
            possible_names = ['Segment', 'segment', 'SEGMENT', 'Market Segment']
            
            for col_name in possible_names:
                if col_name in df.columns:
                    segment_column = col_name
                    break
            
            if segment_column is None:
                print(f"  Warning: 'Segment' column not found, skipping...")
                print(f"  Available columns: {', '.join(df.columns[:15])}...")
                continue
            
            # Count systems by segment
            segment_counts = df[segment_column].value_counts().to_dict()
            
            # Create result entry
            result = {
                'List': list_id,
                'Date': date_code,
                'Total_Systems': len(df)
            }
            
            # Add segment counts
            for segment, count in segment_counts.items():
                if pd.isna(segment):
                    segment_str = 'Unknown'
                else:
                    segment_str = str(segment).strip()
                
                result[f'Segment_{segment_str.replace(" ", "_").replace("/", "_")}'] = count
            
            results.append(result)
            
        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    # Create DataFrame from results
    results_df = pd.DataFrame(results)
    
    # Fill NaN values with 0 (segments that don't appear in all lists)
    results_df = results_df.fillna(0)
    
    # Convert segment columns to integers
    for col in results_df.columns:
        if col.startswith('Segment_'):
            results_df[col] = results_df[col].astype(int)
    
    # Save to CSV
    results_df.to_csv(output_file, index=False)
    
    return results_df

if __name__ == "__main__":
    df = extract_segment_distribution()
