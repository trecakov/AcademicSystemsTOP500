#
# This script extracts academic hpc count from a directory and outputs the csv file.
# It outputs date amd number of academic systems over the years.
#
# To run script 'python3.6 academic_hpcs_over_years.py'
#

import argparse
import os
import pandas as pd
import re

parser = argparse.ArgumentParser(
    description="Count academic HPC systems (row counts) per list from a lists directory"
)
parser.add_argument("input_dir", help="Path to directory containing academic TOP500 lists CSV files")
parser.add_argument(
    "-o", "--output",
    default="academic_counts_over_time.csv",
    help="Path to output CSV file (default: academic_counts_over_time.csv)"
)
args = parser.parse_args()

directory = args.input_dir
data = []

pattern = re.compile(r"TOP500_(\d{6})\.csv")

for file in os.listdir(directory):
    match = pattern.match(file)
    if match:
        date = match.group(1)
        path = os.path.join(directory, file)
        rows = sum(1 for _ in open(path, encoding="utf-8")) - 1
        data.append((date, rows))

df = pd.DataFrame(data, columns=["Date", "RowsKept"]).sort_values("Date")
df.to_csv(args.output, index=False)

print(df)
