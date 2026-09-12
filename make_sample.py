"""
Create a small sample of the Trip table for committing to git.

The full dataset (data/trips.parquet) is large and is NOT committed.  This
script draws a random sample of trips and writes data/sample.csv, which is the
only data file tracked by git.

Usage
-----
    python make_sample.py            # 1000 trips, seed 42
    python make_sample.py -n 5000    # 5000 trips
"""

import argparse
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
TRIPS_PATH = DATA_DIR / "trips.parquet"
SAMPLE_PATH = DATA_DIR / "sample.csv"

DEFAULT_N = 1000
DEFAULT_SEED = 42


def make_sample(n: int = DEFAULT_N, seed: int = DEFAULT_SEED) -> pd.DataFrame:
    trips = pd.read_parquet(TRIPS_PATH)

    n = min(n, len(trips))
    sample = trips.sample(n=n, random_state=seed).reset_index(drop=True)

    # Renumber Trip.ID to 0, 1, 2, ... so the sample is a self-consistent
    # mini Trip table (the spec assigns IDs starting at 0).
    sample["Trip.ID"] = range(n)
    return sample


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--num", type=int, default=DEFAULT_N,
                        help=f"number of trips to sample (default {DEFAULT_N})")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help=f"random seed (default {DEFAULT_SEED})")
    args = parser.parse_args()

    sample = make_sample(args.num, args.seed)
    sample.to_csv(SAMPLE_PATH, index=False)

    print(f"sampled {len(sample)} trips -> {SAMPLE_PATH}")
    print(sample.head())


if __name__ == "__main__":
    main()
