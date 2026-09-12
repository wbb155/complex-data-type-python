"""
Preprocess NYC Yellow Taxi trip records into a Trip table.

The source file (data/yellow_tripdata_2026-01.parquet) records each trip with a
pickup and a dropoff datetime expressed in Eastern Standard Time (New York,
UTC-5).  We convert those to Unix epoch seconds (UTC) and emit a three-column
table:

    Trip.ID    (int) : trip identifier, 0, 1, 2, ... in original file order
    Trip.start (int) : pick-up time, seconds since 1970-01-01 00:00:00 UTC
    Trip.end   (int) : drop-off time, seconds since 1970-01-01 00:00:00 UTC

Because the recorded times are in EST (UTC-5), 5 hours are added to obtain the
UTC instant before converting to epoch seconds.

Example
-------
    tpep_pickup_datetime = 2026-01-01 00:54:04 (EST)
    -> 2026-01-01 05:54:04 UTC
    -> 1767246844 seconds since the epoch

The result is written to data/ as both Parquet (trips.parquet, compact and
fast to load) and CSV (trips.csv, human readable).
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"

SRC_PATH = DATA_DIR / "yellow_tripdata_2026-01.parquet"
OUT_PARQUET = DATA_DIR / "trips.parquet"
OUT_CSV = DATA_DIR / "trips.csv"

# EST is UTC-5, so add 5 hours to move from local EST to UTC.
EST_TO_UTC = pd.Timedelta(hours=5)

PICKUP = "tpep_pickup_datetime"
DROPOFF = "tpep_dropoff_datetime"


def to_unix_seconds(series: pd.Series) -> pd.Series:
    """Convert a naive EST datetime series to integer Unix epoch seconds (UTC)."""
    utc = series + EST_TO_UTC
    # datetime64[s] avoids depending on the input resolution (us/ns) and
    # truncates any sub-second component; all values here are whole seconds.
    return utc.astype("datetime64[s]").astype("int64")


def build_trips(src_path: Path = SRC_PATH) -> pd.DataFrame:
    df = pd.read_parquet(src_path, columns=[PICKUP, DROPOFF])

    trips = pd.DataFrame(
        {
            "Trip.ID": range(len(df)),
            "Trip.start": to_unix_seconds(df[PICKUP]).to_numpy(),
            "Trip.end": to_unix_seconds(df[DROPOFF]).to_numpy(),
        }
    )
    return trips


def main() -> None:
    trips = build_trips()

    trips.to_parquet(OUT_PARQUET, index=False)
    trips.to_csv(OUT_CSV, index=False)

    print(f"trips : {len(trips)}")
    print(trips.head())
    print(f"wrote : {OUT_PARQUET}")
    print(f"wrote : {OUT_CSV}")


if __name__ == "__main__":
    main()
