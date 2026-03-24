import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
ASSETS_DIR = Path(__file__).parent.parent / "assets"
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────
def load_data():
    region_df = pd.read_csv(PROCESSED_DIR / "all_regions.csv")
    time_df = pd.read_csv(PROCESSED_DIR / "all_time_series.csv", parse_dates=["date"])
    gdf = gpd.read_file(ASSETS_DIR / "uk_nations.geojson")
    gdf = gdf.rename(columns={"CTRY23NM": "region"})
    return region_df, time_df, gdf


# ── Chart 1: Choropleth map ───────────────────────────────────────
def plot_choropleth(region_df, gdf, keyword, save=True):
    """
    Plot a choropleth map of UK nations coloured by search interest
    for a given keyword.
    """
    # Filter to keyword and average interest across time
    kw_df = region_df[region_df["keyword"] == keyword][["region", "interest"]]

    # Merge with geodataframe
    merged = gdf.merge(kw_df, on="region", how="left")

    fig, ax = plt.subplots(1, 1, figsize=(6, 8))
    merged.plot(
        column="interest",
        ax=ax,
        legend=True,
        cmap="Blues",
        edgecolor="white",
        linewidth=0.8,
        missing_kwds={"color": "lightgrey", "label": "No data"},
    )

    ax.set_title(f'Search interest: "{keyword}"', fontsize=14, fontweight="bold", pad=12)
    ax.set_axis_off()

    plt.tight_layout()

    if save:
        path = OUTPUT_DIR / f"map_{keyword.replace(' ', '_')}.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  Saved → {path}")

    return fig


# ── Chart 2: Time series ──────────────────────────────────────────
def plot_time_series(time_df, category, save=True):
    """
    Plot search interest over time for all keywords in a category.
    """
    df = time_df[time_df["category"] == category]

    fig, ax = plt.subplots(figsize=(12, 5))

    for keyword, group in df.groupby("keyword"):
        ax.plot(group["date"], group["interest"], label=keyword, linewidth=1.5)

    ax.set_title(f'Search interest over time — {category.replace("_", " ").title()}',
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Interest (0–100)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    if save:
        path = OUTPUT_DIR / f"timeseries_{category}.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  Saved → {path}")

    return fig


# ── Chart 3: Bar chart — top keyword per nation ───────────────────
def plot_top_keywords_by_nation(region_df, save=True):
    """
    For each nation, plot the top keyword by average interest.
    """
    top = (
        region_df.groupby(["region", "keyword"])["interest"]
        .mean()
        .reset_index()
        .sort_values("interest", ascending=False)
        .groupby("region")
        .head(5)
    )

    nations = top["region"].unique()
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
              "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]

    for i, nation in enumerate(sorted(nations)):
        ax = axes[i]
        data = top[top["region"] == nation].sort_values("interest")
        ax.barh(data["keyword"], data["interest"],
                color=colors[:len(data)], edgecolor="white")
        ax.set_title(nation, fontsize=13, fontweight="bold")
        ax.set_xlabel("Average interest (0–100)")
        ax.grid(axis="x", alpha=0.3)

    plt.suptitle("Top searched keywords by UK nation (5-year average)",
                 fontsize=15, fontweight="bold", y=1.01)
    plt.tight_layout()

    if save:
        path = OUTPUT_DIR / f"top_keywords_by_nation.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  Saved → {path}")

    return fig


# ── Main ──────────────────────────────────────────────────────────
def main():
    print("Loading data...")
    region_df, time_df, gdf = load_data()

    print("\nGenerating choropleth maps...")
    for keyword in ["food bank", "NHS waiting times", "Premier League"]:
        plot_choropleth(region_df, gdf, keyword)

    print("\nGenerating time series charts...")
    for category in ["cost_of_living", "health_nhs", "sport"]:
        plot_time_series(time_df, category)

    print("\nGenerating top keywords by nation...")
    plot_top_keywords_by_nation(region_df)

    print("\nDone. All charts saved to assets/charts/")


if __name__ == "__main__":
    main()