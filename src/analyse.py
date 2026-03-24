import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from statsmodels.tsa.seasonal import seasonal_decompose
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Keywords best suited to seasonal decomposition ────────────────
# These have strong, recurring yearly patterns
SEASONAL_KEYWORDS = [
    "Wimbledon",
    "Premier League",
    "Six Nations",
    "cost of living",
    "mental health",
    "GP appointment",
]


def load_time_series() -> pd.DataFrame:
    return pd.read_csv(
        PROCESSED_DIR / "all_time_series.csv", parse_dates=["date"]
    )


def decompose_keyword(df: pd.DataFrame, keyword: str) -> dict:
    """
    Run seasonal decomposition on a single keyword.
    Returns a dict with the decomposition result and the original series.
    """
    series = (
        df[df["keyword"] == keyword]
        .set_index("date")["interest"]
        .resample("W")
        .mean()
        .fillna(method="ffill")
    )

    # Need at least 2 full cycles — 52 weeks per year, period=52
    if len(series) < 104:
        print(f"  Skipping {keyword} — not enough data")
        return None

    result = seasonal_decompose(series, model="additive", period=52)
    return {"series": series, "result": result, "keyword": keyword}


def plot_decomposition(decomp: dict, save=True) -> plt.Figure:
    """
    Plot the original series, trend, seasonal, and residual
    components in a clean 4-panel chart.
    """
    keyword = decomp["keyword"]
    result = decomp["result"]
    series = decomp["series"]

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        f'Seasonal decomposition — "{keyword}"',
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )

    gs = gridspec.GridSpec(4, 1, hspace=0.5)

    # Panel 1 — observed
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(series, color="#1f77b4", linewidth=1.2)
    ax1.set_ylabel("Observed", fontsize=10)
    ax1.grid(axis="y", alpha=0.3)
    ax1.set_xticklabels([])

    # Panel 2 — trend
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(result.trend, color="#2ca02c", linewidth=1.5)
    ax2.set_ylabel("Trend", fontsize=10)
    ax2.grid(axis="y", alpha=0.3)
    ax2.set_xticklabels([])

    # Panel 3 — seasonal
    ax3 = fig.add_subplot(gs[2])
    ax3.plot(result.seasonal, color="#ff7f0e", linewidth=1.2)
    ax3.set_ylabel("Seasonal", fontsize=10)
    ax3.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax3.grid(axis="y", alpha=0.3)
    ax3.set_xticklabels([])

    # Panel 4 — residual
    ax4 = fig.add_subplot(gs[3])
    ax4.plot(result.resid, color="#d62728", linewidth=0.8, alpha=0.7)
    ax4.set_ylabel("Residual", fontsize=10)
    ax4.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax4.grid(axis="y", alpha=0.3)
    ax4.set_xlabel("Date", fontsize=10)

    if save:
        safe_name = keyword.replace(" ", "_").replace("/", "_")
        path = OUTPUT_DIR / f"decomp_{safe_name}.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  Saved → {path}")

    return fig


def plot_seasonal_summary(df: pd.DataFrame, save=True) -> plt.Figure:
    """
    Plot the average seasonal pattern (by week of year) for each
    keyword on a single chart — great for the dashboard overview.
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    for keyword in SEASONAL_KEYWORDS:
        series = (
            df[df["keyword"] == keyword]
            .set_index("date")["interest"]
            .resample("W")
            .mean()
            .fillna(method="ffill")
        )

        if len(series) < 104:
            continue

        result = seasonal_decompose(series, model="additive", period=52)

        # Average seasonal effect by week of year
        seasonal_df = result.seasonal.copy()
        seasonal_df.index = seasonal_df.index.isocalendar().week.astype(int)
        weekly_avg = seasonal_df.groupby(seasonal_df.index).mean()

        ax.plot(weekly_avg.index, weekly_avg.values, label=keyword, linewidth=1.8)

    ax.set_title(
        "Average seasonal pattern by week of year",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Week of year", fontsize=11)
    ax.set_ylabel("Seasonal effect (relative to trend)", fontsize=11)
    ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # Label key months along x axis
    month_weeks = {1: "Jan", 9: "Mar", 18: "May", 27: "Jul",
                   36: "Sep", 44: "Nov", 52: "Dec"}
    ax.set_xticks(list(month_weeks.keys()))
    ax.set_xticklabels(list(month_weeks.values()))

    plt.tight_layout()

    if save:
        path = OUTPUT_DIR / "seasonal_summary.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  Saved → {path}")

    return fig


def main():
    print("Loading time series data...")
    df = load_time_series()

    print("\nRunning seasonal decomposition...")
    for keyword in SEASONAL_KEYWORDS:
        print(f"  Processing: {keyword}")
        decomp = decompose_keyword(df, keyword)
        if decomp:
            plot_decomposition(decomp)

    print("\nGenerating seasonal summary chart...")
    plot_seasonal_summary(df)

    print("\nDone. All charts saved to assets/charts/")


if __name__ == "__main__":
    main()