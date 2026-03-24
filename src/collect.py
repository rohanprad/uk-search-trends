import time
import pandas as pd
from pytrends.request import TrendReq
from pathlib import Path

# ── Output directory ──────────────────────────────────────────────
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ── Timeframe ─────────────────────────────────────────────────────
TIMEFRAME = "today 5-y"

# ── UK regions (pytrends geo codes) ───────────────────────────────
GEO = "GB"

# ── Keyword categories ────────────────────────────────────────────
CATEGORIES = {
    "cost_of_living": [
        "food bank",
        "energy bills",
        "mortgage rates",
        "inflation UK",
        "cost of living",
    ],
    "health_nhs": [
        "GP appointment",
        "NHS waiting times",
        "mental health",
        "A&E",
        "prescription charges",
    ],
    "entertainment_culture": [
        "Netflix",
        "Spotify",
        "cinema",
        "festival tickets",
        "streaming",
    ],
    "politics_news": [
        "general election",
        "Keir Starmer",
        "Reform UK",
        "House of Commons",
        "Brexit",
    ],
    "jobs_economy": [
        "job vacancies",
        "Universal Credit",
        "minimum wage",
        "redundancy",
        "work from home",
    ],
    "sport": [
        "Premier League",
        "Six Nations",
        "The Ashes",
        "Wimbledon",
        "Formula 1",
    ],
}


def build_pytrends() -> TrendReq:
    """Initialise pytrends session."""
    return TrendReq(hl="en-GB", tz=0)


def fetch_interest_over_time(
    pytrends: TrendReq, keywords: list, category_name: str
) -> None:
    """Fetch national time series for a keyword group and save to CSV."""
    print(f"  [time] {category_name}")
    pytrends.build_payload(keywords, geo=GEO, timeframe=TIMEFRAME)
    df = pytrends.interest_over_time()

    if df.empty:
        print(f"  WARNING: no data for {category_name}")
        return

    df = df.drop(columns=["isPartial"], errors="ignore")
    df.to_csv(RAW_DIR / f"{category_name}_time.csv")
    print(f"  Saved → data/raw/{category_name}_time.csv")


def fetch_interest_by_region(
    pytrends: TrendReq, keywords: list, category_name: str
) -> None:
    """Fetch regional breakdown for a keyword group and save to CSV."""
    print(f"  [region] {category_name}")
    pytrends.build_payload(keywords, geo=GEO, timeframe=TIMEFRAME)
    df = pytrends.interest_by_region(resolution="REGION", inc_low_vol=True)

    if df.empty:
        print(f"  WARNING: no regional data for {category_name}")
        return

    df.to_csv(RAW_DIR / f"{category_name}_region.csv")
    print(f"  Saved → data/raw/{category_name}_region.csv")


def main():
    pytrends = build_pytrends()

    for category_name, keywords in CATEGORIES.items():
        print(f"\nCategory: {category_name}")

        fetch_interest_over_time(pytrends, keywords, category_name)
        time.sleep(5)  # avoid rate limiting

        fetch_interest_by_region(pytrends, keywords, category_name)
        time.sleep(5)  # avoid rate limiting

    print("\nDone. All files saved to data/raw/")


if __name__ == "__main__":
    main()