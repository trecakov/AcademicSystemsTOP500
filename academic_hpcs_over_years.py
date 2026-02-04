#
# This script extracts academic hpc count from AllListsAcademia directory and outputs the csv file.
#
# It outputs date amd number of academic systems over the years.
#
# To run script 'python3.6 academic_hpcs_over_years.py'
#

import os
import pandas as pd
import re

directory = "AllListsAcademia"
data = []

pattern = re.compile(r"TOP500_(\d{6})A\.csv")

for file in os.listdir(directory):
    match = pattern.match(file)
    if match:
        date = match.group(1)
        path = os.path.join(directory, file)
        rows = sum(1 for _ in open(path, encoding="utf-8")) - 1
        data.append((date, rows))

df = pd.DataFrame(data, columns=["Date", "RowsKept"]).sort_values("Date")
df.to_csv("academic_counts_over_time.csv", index=False)

print(df)

