import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def parse_memory_to_MB(series: pd.Series) -> pd.Series:
    """Convert strings like '1.5 GB', '12.4 MB', '0', etc. to MB (vectorized)."""

    # Replace NaN with "0", strip spaces, and convert to uppercase
    s = series.fillna("0").str.strip().str.upper()

    # Extract the numeric value and unit using a single regex
    extracted = s.str.extract(r'(?P<num>[\d\.]+)\s*(?P<unit>GB|MB)?')

    # Convert the numeric part to float
    extracted['num'] = extracted['num'].astype(float)

    # Default missing units to MB
    extracted['unit'] = extracted['unit'].fillna("MB")

    # Calculate memory in MB
    extracted['MB'] = extracted['num'] * extracted['unit'].map({'GB': 1024, 'MB': 1})

    # Replace any remaining NaN with 0.0
    return extracted['MB'].fillna(0.0)


def parse_cpu(series: pd.Series) -> pd.Series:
    """Convert '%cpu' strings like '97.8%', '-', or NaN to a ceil integer after dividing by 100."""

    # Replace "-" and NaN with "0", convert to string, and remove the "%" sign
    s = series.fillna("0").astype(str).str.replace("-", "0").str.rstrip("%")

    # Convert to float, replacing any errors with 0
    s_float = pd.to_numeric(s, errors='coerce').fillna(0)

    # Divide by 100 and apply ceil vectorized, then convert to int
    return np.ceil(s_float / 100).astype(int)


def parse_time_to_minutes(series: pd.Series) -> pd.Series:
    """
    Convert time strings like "3s", "4m 32s", "500ms", "1h 2m 30s"
    into total minutes (float), rounded to 1 decimal, vectorized.
    """

    # Ensure the input is a string, fill NaN with empty string, lowercase and strip spaces
    s = series.fillna("").astype(str).str.lower().str.strip()

    # Extract all (value, unit) pairs from each string using regex
    all_matches = s.str.extractall(r'(\d+\.?\d*)\s*(ms|s|m|h)')

    # Convert the numeric values to float and replace any non-numeric with 0
    all_matches[0] = pd.to_numeric(all_matches[0], errors='coerce').fillna(0)

    # Map each unit to its conversion factor to minutes
    factor = {'ms': 1 / (1000 * 60), 's': 1 / 60, 'm': 1, 'h': 60}

    # Calculate minutes for each extracted pair
    all_matches['minutes'] = all_matches[0] * all_matches[1].map(factor)

    # Group by the original row index and sum all minutes for that row
    total_minutes = all_matches.groupby(level=0)['minutes'].sum()

    # Reindex to match the original Series and fill missing values with 0, then round to 1 decimal
    return total_minutes.reindex(series.index, fill_value=0).round(1)


def get_process_name(series: pd.Series) -> pd.Series:
    """
    Extract the process name from a string like 'process_name (details)'
    using vectorized operations.
    """
    # Ensure the input is a string, fill NaN with empty string, and strip spaces
    s = series.fillna("").astype(str).str.strip()

    # Apply vectorized regex:
    # Capture the last block of characters that is not a space, parenthesis, or colon
    return s.str.extract(r'([^:()\s]+)\s*(?:\([^)]*\))?$')[0]


# Custom aggregation function for percentiles
def percentile(p):
    return lambda x: np.percentile(x, p)


def main(file_path: str, out_dir: str):
    # Read only the necessary columns from the CSV
    df = pd.read_csv(
        file_path,
        sep="\t",
        usecols=["name", "realtime", "%cpu", "peak_rss", "status"]
    )
    df = df[df["status"] == "COMPLETED"]

    # Create the final DataFrame directly with the processed columns
    cleaned_df = pd.DataFrame({
        "process_name": get_process_name(df["name"]),  # Extract process names
        "memory_MB": parse_memory_to_MB(df["peak_rss"]),  # Convert memory to MB
        "cpus": parse_cpu(df["%cpu"]),  # Parse CPU usage and ceil
        "minutes": parse_time_to_minutes(df["realtime"])  # Convert time to minutes
    })

    summary_df = cleaned_df.groupby("process_name").agg(
        cpu_min=("cpus", "min"),
        cpu_max=("cpus", "max"),
        cpu_p50=("cpus", percentile(50)),
        cpu_p90=("cpus", percentile(90)),
        cpu_p99=("cpus", percentile(99)),

        minutes_min=("minutes", "min"),
        minutes_max=("minutes", "max"),
        minutes_p50=("minutes", percentile(50)),
        minutes_p90=("minutes", percentile(90)),
        minutes_p99=("minutes", percentile(99)),

        memory_MB_min=("memory_MB", "min"),
        memory_MB_max=("memory_MB", "max"),
        memory_MB_p50=("memory_MB", percentile(50)),
        memory_MB_p90=("memory_MB", percentile(90)),
        memory_MB_p99=("memory_MB", percentile(99)),
    ).reset_index()

    # Write output file
    out_dir = Path(out_dir)
    out_dir.mkdir(parents = True, exist_ok = True)
    out_path = Path(out_dir).joinpath(f"summary_{Path(file_path).stem}.csv")

    summary_df.to_csv(out_path, index = False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarise an execution trace file")
    parser.add_argument("-f", "--filename", type=str,
                        help="Path to the input execution trace file")
    parser.add_argument("-o", "--outdir", type=str, default=".",
                        help="Output directory")

    args = parser.parse_args()

    main(args.filename, args.outdir)
