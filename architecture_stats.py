#
# This script extracts architecture, CPU-brand, and GPU-brand statistics from the
# AllListsAcademia directory and outputs a CSV file.
#
# For each TOP500 list (2011-2025) it counts:
#   - Architecture type: MPP vs Cluster (and any "Other" it doesn't recognize)
#   - CPU brand: AMD, Intel, IBM Power, ARM/Other  (inferred from the Processor /
#     Processor Technology text fields)
#   - GPU brand: NVIDIA, AMD, Intel, Other  (inferred from the
#     Accelerator/Co-Processor text field; systems with no accelerator are not counted)
#
# Example of the kind of summary it produces, for list 202511:
#   13 MPP, 56 Cluster; CPUs: 30 AMD, 30 Intel, 9 IBM Power; GPUs: 20 NVIDIA, 10 AMD
#
# To run: 'python3 architecture_brands.py'
#

import pandas as pd
import os
import glob
import re


# ----------------------------------------------------------------------------
# Helpers to locate columns by trying several likely names
# ----------------------------------------------------------------------------
def find_column(df, candidates, substring_fallback=None):
    """Return the first column in `candidates` that exists in df, else the first
    column whose lowercased name contains `substring_fallback`."""
    for name in candidates:
        if name in df.columns:
            return name
    if substring_fallback:
        for col in df.columns:
            if substring_fallback in col.lower():
                return col
    return None


# ----------------------------------------------------------------------------
# Classifiers: map a free-text field to a normalized brand / type
# ----------------------------------------------------------------------------
def classify_architecture(value):
    if pd.isna(value):
        return "Unknown"
    v = str(value).strip().lower()
    if v == "" or v == "none":
        return "Unknown"
    if "mpp" in v:
        return "MPP"
    if "cluster" in v:
        return "Cluster"
    if "constellation" in v:
        return "Constellation"
    if "smp" in v:
        return "SMP"
    return "Other"


def classify_cpu(*values):
    """Infer CPU brand from one or more text fields (Processor, Processor
    Technology). Checks in priority order so e.g. an AMD EPYC isn't mislabeled."""
    text = " ".join(str(v) for v in values if pd.notna(v)).lower()
    if text.strip() == "" or text.strip() == "none":
        return "Unknown"
    # NVIDIA Grace (and Grace-Hopper "GH" superchips) — ARM-based NVIDIA CPU.
    # Checked before the generic ARM bucket so it gets its own brand.
    if "grace" in text or re.search(r"\bgh\b", text) or "gh superchip" in text:
        return "NVIDIA Grace"
    # IBM Power first: "power" is distinctive and avoids "powerpc" confusion later
    if "power" in text or "ibm" in text:
        return "IBM Power"
    if "amd" in text or "epyc" in text or "opteron" in text:
        return "AMD"
    if "intel" in text or "xeon" in text or "knight" in text or "phi" in text \
            or "core i" in text or "pentium" in text or "itanium" in text:
        return "Intel"
    if "arm" in text or "graviton" in text or "a64fx" in text \
            or "neoverse" in text or "fujitsu" in text or "sparc" in text:
        return "Other"
    if "vector engine" in text or "nec" in text or "sx-aurora" in text:
        return "Other"
    return "Other"


def classify_gpu(*values):
    """Infer GPU/accelerator brand from text fields. Returns None when there is
    no accelerator (so the system is not counted in GPU totals)."""
    text = " ".join(str(v) for v in values if pd.notna(v)).lower()
    if text.strip() == "" or text.strip() == "none" or text.strip() == "nan":
        return None
    if "nvidia" in text or "tesla" in text or "volta" in text or "ampere" in text \
            or "hopper" in text or "kepler" in text or "pascal" in text \
            or "fermi" in text or text.strip().startswith("gpu") \
            or re.search(r"\bh100\b|\ba100\b|\bv100\b|\bp100\b|\bk[0-9]{2}\b|\bgh200\b", text):
        return "NVIDIA"
    if "instinct" in text or "radeon" in text or "ati " in text \
            or re.search(r"\bmi[0-9]{2,3}\b", text) \
            or "firepro" in text or ("amd" in text and "gpu" in text):
        return "AMD"
    if "ponte vecchio" in text or "data center gpu" in text or "max " in text \
            or "xe " in text or ("intel" in text and "gpu" in text) \
            or "knight" in text or "phi" in text:
        # Note: Xeon Phi / Knights * were co-processors; counted here as Intel accel.
        return "Intel"
    if "matrix" in text or "pezy" in text or "sw26010" in text:
        return "Other"
    # Has *something* in the accelerator field but unrecognized brand
    return "Other"


def extract_architecture_brand_statistics(input_dir="AllListsAcademia",
                                          output_file="architecture_brand_statistics.csv"):
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))

    # Filter files from 2011 to 2025
    filtered_files = []
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        date_match = re.search(r"(\d{6})", filename)
        if date_match:
            date_code = int(date_match.group(1))
            year = date_code // 100
            if 2011 <= year <= 2025:
                filtered_files.append(csv_file)

    if not filtered_files:
        print(f"No CSV files found from 2011-2025 in {input_dir}")
        return

    print(f"Found {len(filtered_files)} CSV files from 2011-2025")

    # Fixed category orders so the output columns are stable
    arch_types = ["MPP", "Cluster", "Constellation", "SMP", "Other", "Unknown"]
    cpu_brands = ["AMD", "Intel", "IBM Power", "NVIDIA Grace", "Other", "Unknown"]
    gpu_brands = ["NVIDIA", "AMD", "Intel", "Other"]

    results = []

    for csv_file in sorted(filtered_files):
        try:
            filename = os.path.basename(csv_file)
            list_id = os.path.splitext(filename)[0]
            date_match = re.search(r"(\d{6})", list_id)
            date_code = date_match.group(1) if date_match else None

            print(f"\nProcessing {filename} (date code: {date_code})")

            df = pd.read_csv(csv_file)

            # Locate the relevant text columns
            arch_col = find_column(
                df,
                ["Architecture", "System Architecture", "Arch"],
                substring_fallback="architectur",
            )
            proc_col = find_column(
                df,
                ["Processor", "CPU", "Processor Name"],
                substring_fallback="processor",
            )
            proc_tech_col = find_column(
                df,
                ["Processor Technology", "Processor Generation", "Processor Family"],
                substring_fallback="technolog",
            )
            accel_col = find_column(
                df,
                ["Accelerator/Co-Processor", "Accelerator/Co-processor",
                 "Accelerator", "Co-Processor", "Coprocessor"],
                substring_fallback="accelerator",
            )

            if arch_col is None:
                print("  Warning: no Architecture column found.")
            if proc_col is None and proc_tech_col is None:
                print("  Warning: no Processor column found.")
            if accel_col is None:
                print("  Warning: no Accelerator column found (GPU counts will be 0).")

            # Initialize counters
            arch_counts = {k: 0 for k in arch_types}
            cpu_counts = {k: 0 for k in cpu_brands}
            gpu_counts = {k: 0 for k in gpu_brands}
            systems_with_accel = 0

            for _, row in df.iterrows():
                # Architecture
                if arch_col is not None:
                    arch_counts[classify_architecture(row[arch_col])] += 1
                else:
                    arch_counts["Unknown"] += 1

                # CPU brand
                proc_val = row[proc_col] if proc_col is not None else None
                proc_tech_val = row[proc_tech_col] if proc_tech_col is not None else None
                cpu_counts[classify_cpu(proc_val, proc_tech_val)] += 1

                # GPU brand (only systems that actually have an accelerator)
                if accel_col is not None:
                    gpu = classify_gpu(row[accel_col])
                    if gpu is not None:
                        gpu_counts[gpu] += 1
                        systems_with_accel += 1

            record = {
                "List": list_id,
                "Date": date_code,
                "Total_Systems": len(df),
                "Systems_With_Accelerator": systems_with_accel,
            }
            for k in arch_types:
                record[f"Arch_{k.replace(' ', '_')}"] = arch_counts[k]
            for k in cpu_brands:
                record[f"CPU_{k.replace(' ', '_').replace('/', '_')}"] = cpu_counts[k]
            for k in gpu_brands:
                record[f"GPU_{k.replace(' ', '_')}"] = gpu_counts[k]

            results.append(record)

            # Print a human-readable summary like your example
            arch_summary = ", ".join(
                f"{arch_counts[k]} {k}" for k in arch_types if arch_counts[k] > 0
            )
            cpu_summary = ", ".join(
                f"{cpu_counts[k]} {k}" for k in cpu_brands if cpu_counts[k] > 0
            )
            gpu_summary = ", ".join(
                f"{gpu_counts[k]} {k}" for k in gpu_brands if gpu_counts[k] > 0
            )
            print(f"  Architecture: {arch_summary}")
            print(f"  CPUs: {cpu_summary}")
            print(f"  GPUs: {gpu_summary if gpu_summary else 'none'}")

        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    print(f"\nSaved statistics to {output_file}")
    return results_df


if __name__ == "__main__":
    df = extract_architecture_brand_statistics()
