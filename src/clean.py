import pandas as pd
from pathlib import Path

# ── Directories ───────────────────────────────────────────────────
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ── Category names (must match filenames in data/raw) ─────────────
CATEGORIES = [
    "cost_of_living",
    "health_nhs",
    "entertainment_culture",
    "politics_news",
    "jobs_economy",
    "sport",
]


def clean_time_series(category: str) -> pd.DataFrame:
    """
    Load and clean a _time.csv file.
    - Parses dates
    - Drops nulls
    - Adds a category column
    - Melts from wide to long format
    """
    path = RAW_DIR / f"{category}_time.csv"
    df = pd.read_csv(path, index_col="date", parse_dates=True)
    df.index.name = "date"

    # Drop any fully empty columns
    df = df.dropna(axis=1, how="all")

    # Melt from wide (one col per keyword) to long (one row per keyword/date)
    df = df.reset_index()
    df = df.melt(id_vars="date", var_name="keyword", value_name="interest")

    # Add category label
    df["category"] = category

    # Drop rows where interest is null
    df = df.dropna(subset=["interest"])

    return df


def clean_region(category: str) -> pd.DataFrame:
    """
    Load and clean a _region.csv file.
    - Adds a category column
    - Melts from wide to long format
    - Normalises region names
    """
    path = RAW_DIR / f"{category}_region.csv"
    df = pd.read_csv(path, index_col="geoName")
    df.index.name = "region"

    # Drop any fully empty columns
    df = df.dropna(axis=1, how="all")

    # Melt from wide to long format
    df = df.reset_index()
    df = df.melt(id_vars="region", var_name="keyword", value_name="interest")

    # Add category label
    df["category"] = category

    # Drop rows where interest is null
    df = df.dropna(subset=["interest"])

    # Normalise region names to title case
    df["region"] = df["region"].str.title()

    return df


def build_combined_time_series() -> pd.DataFrame:
    """Combine all category time series into one master DataFrame."""
    frames = [clean_time_series(cat) for cat in CATEGORIES]
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values(["category", "keyword", "date"])
    df = df.reset_index(drop=True)
    return df


def build_combined_region() -> pd.DataFrame:
    """Combine all category region data into one master DataFrame."""
    frames = [clean_region(cat) for cat in CATEGORIES]
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values(["category", "keyword", "region"])
    df = df.reset_index(drop=True)
    return df


def main():
    print("Cleaning time series data...")
    time_df = build_combined_time_series()
    time_df.to_csv(PROCESSED_DIR / "all_time_series.csv", index=False)
    print(f"  Saved → data/processed/all_time_series.csv ({len(time_df):,} rows)")

    print("Cleaning regional data...")
    region_df = build_combined_region()
    region_df.to_csv(PROCESSED_DIR / "all_regions.csv", index=False)
    print(f"  Saved → data/processed/all_regions.csv ({len(region_df):,} rows)")

    print("\nDone. Processed files ready in data/processed/")

    # Quick sanity check
    print("\n── Time series preview ──")
    print(time_df.head(10).to_string())
    print("\n── Region preview ──")
    print(region_df.head(10).to_string())

    print("\n── Regions found ──")
    print(sorted(region_df["region"].unique()))


if __name__ == "__main__":
    main()