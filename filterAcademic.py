# 
# This script splits TOP500lists files by the 'Segment' column into academic(TOP500Academic/) and non-academic(TOP500withoutAcademic/)
#
# To run script 'python3.6 filterAcademic.py TOP500lists/'
#

import argparse
import os
import pandas as pd

ACADEMIC_DIR = "TOP500Academic"
NON_ACADEMIC_DIR = "TOP500withoutAcademic"
SUPPORTED_EXTS = (".csv", ".xlsx", ".xls")


def load_with_detected_header(file_path, ext):
    # Read without header
    if ext == ".csv":
        temp_df = pd.read_csv(file_path, header=None)
    elif ext == ".xlsx":
        temp_df = pd.read_excel(file_path, header=None, engine="openpyxl")
    elif ext == ".xls":
        temp_df = pd.read_excel(file_path, header=None, engine="xlrd")
    else:
        raise ValueError("Unsupported file type")

    # Header row containing 'Segment'
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


def split_academic(input_file):
    base, ext = os.path.splitext(input_file)
    ext = ext.lower()
    filename = os.path.basename(base)

    os.makedirs(ACADEMIC_DIR, exist_ok=True)
    os.makedirs(NON_ACADEMIC_DIR, exist_ok=True)

    academic_output = os.path.join(ACADEMIC_DIR, f"{filename}.csv")
    non_academic_output = os.path.join(NON_ACADEMIC_DIR, f"{filename}.csv")

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

    academic_df = df[df["Segment"] == "Academic"]
    non_academic_df = df[df["Segment"] != "Academic"]

    academic_df.to_csv(academic_output, index=False)
    non_academic_df.to_csv(non_academic_output, index=False)

    print(f"Wrote {academic_output} ({len(academic_df)} rows)")
    print(f"Wrote {non_academic_output} ({len(non_academic_df)} rows)")


def process_path(input_path):
    if os.path.isdir(input_path):
        # Process every supported file in the directory
        files = sorted(
            f for f in os.listdir(input_path)
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS
        )
        if not files:
            print(f"No supported files ({', '.join(SUPPORTED_EXTS)}) found in {input_path}")
            return
        for f in files:
            full_path = os.path.join(input_path, f)
            try:
                split_academic(full_path)
            except Exception as e:
                print(f"Skipping {full_path}: {e}")
    else:
        split_academic(input_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split rows by Segment == 'Academic' into TOP500Academic/ and TOP500withoutAcademic/ (CSV, XLSX, XLS)"
    )
    parser.add_argument("input_path", help="Path to an input file or a directory of files")
    args = parser.parse_args()

    process_path(args.input_path)
