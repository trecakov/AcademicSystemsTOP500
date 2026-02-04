#
# This script filters academic hpcs from AllLists directory and TOP500 lists; and outputs the academic lists.
#
# To run script 'python3.6 filterAcademic.py'
#

import argparse
import os
import pandas as pd

def load_with_detected_header(file_path, ext):
    # Read without header first
    if ext == ".csv":
        temp_df = pd.read_csv(file_path, header=None)
    elif ext == ".xlsx":
        temp_df = pd.read_excel(file_path, header=None, engine="openpyxl")
    elif ext == ".xls":
        temp_df = pd.read_excel(file_path, header=None, engine="xlrd")
    else:
        raise ValueError("Unsupported file type")

    # Find header row containing 'Segment'
    header_row = None
    for i in range(min(20, len(temp_df))):
        row_values = temp_df.iloc[i].astype(str).str.strip()
        if "Segment" in row_values.values:
            header_row = i
            break

    if header_row is None:
        raise ValueError("Could not find a header row containing 'Segment'")

    # Re-read using detected header row
    if ext == ".csv":
        return pd.read_csv(file_path, header=header_row)
    elif ext == ".xlsx":
        return pd.read_excel(file_path, header=header_row, engine="openpyxl")
    else:  # .xls
        return pd.read_excel(file_path, header=header_row, engine="xlrd")

def filter_academic(input_file):
    base, ext = os.path.splitext(input_file)
    ext = ext.lower()
    output_file = f"{base}A.csv"

    df = load_with_detected_header(input_file, ext)

    # Clean column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\u00a0", "", regex=False)
    )

    # Enforce Segment column
    if "Segment" not in df.columns:
        raise ValueError(
            f"'Segment' column not found after header detection. Columns: {list(df.columns)}"
        )

    # Filter rows
    filtered_df = df[df["Segment"] == "Academic"]

    # Save output
    filtered_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Filter rows where Segment = Academic (CSV, XLSX, XLS)"
    )
    parser.add_argument("input_file", help="Path to input file")
    args = parser.parse_args()

    filter_academic(args.input_file)
