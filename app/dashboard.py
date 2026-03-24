import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from statsmodels.tsa.seasonal import seasonal_decompose
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent / "src"))
from visualise import plot_choropleth, plot_time_series, plot_top_keywords_by_nation
from analyse import decompose_keyword, plot_decomposition, plot_seasonal_summary

# ── Paths ─────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
ASSETS_DIR = ROOT / "assets"

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="UK Search Trends",
    page_icon="🇬🇧",
    layout="wide",
)

# ── Load data (cached so it only runs once) ───────────────────────
@st.cache_data
def load_data():
    region_df = pd.read_csv(PROCESSED_DIR / "all_regions.csv")
    time_df = pd.read_csv(
        PROCESSED_DIR / "all_time_series.csv", parse_dates=["date"]
    )
    gdf = gpd.read_file(ASSETS_DIR / "uk_nations.geojson")
    gdf = gdf.rename(columns={"CTRY23NM": "region"})
    return region_df, time_df, gdf

region_df, time_df, gdf = load_data()

CATEGORIES = sorted(time_df["category"].unique())
ALL_KEYWORDS = sorted(time_df["keyword"].unique())

# ── Sidebar ───────────────────────────────────────────────────────
st.sidebar.markdown("🇬🇧")
st.sidebar.title("UK Search Trends")
st.sidebar.markdown("Google Trends analysis across the four UK nations · 5 year view")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Map Explorer", "Time Series", "Seasonal Analysis"],
)

# ═══════════════════════════════════════════════════════════════════
# PAGE 1 — Overview
# ═══════════════════════════════════════════════════════════════════
if page == "Overview":
    st.title("UK Google Search Trends")
    st.markdown(
        """
        An analysis of what the four UK nations have been searching for
        over the past 5 years, using Google Trends data via the pytrends API.
        """
    )

    st.divider()

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Keywords tracked", len(ALL_KEYWORDS))
    col2.metric("Categories", len(CATEGORIES))
    col3.metric("Nations", 4)
    col4.metric(
        "Date range",
        f"{time_df['date'].min().year} – {time_df['date'].max().year}",
    )

    st.divider()

    # Top keywords chart
    st.subheader("Top 5 keywords per nation (5-year average)")
    fig = plot_top_keywords_by_nation(region_df, save=False)
    st.pyplot(fig)
    plt.close()

    st.divider()

    # Key findings
    st.subheader("Key findings")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Universal Credit** is the top search in England, Wales and Northern Ireland — reflecting the dominance of welfare concerns across the UK.")
        st.markdown("**Mental health** is the top search in Scotland and second in all other nations, with a consistent upward trend since 2021.")
        st.markdown("**GP appointment** searches have risen steadily year on year — a clear signal of growing NHS access pressure.")

    with col2:
        st.markdown("**Cost of living** searches peaked dramatically in late 2022 during the Liz Truss mini-budget crisis, then declined but remain elevated.")
        st.markdown("**Premier League** search interest has been gradually declining since its 2023 peak.")
        st.markdown("**Wimbledon** shows the most textbook seasonal pattern of any keyword — a perfect annual spike every July.")


# ═══════════════════════════════════════════════════════════════════
# PAGE 2 — Map Explorer
# ═══════════════════════════════════════════════════════════════════
elif page == "Map Explorer":
    st.title("🗺️ Map Explorer")
    st.markdown("Select a keyword to see search interest across the four UK nations.")

    keyword = st.selectbox("Keyword", ALL_KEYWORDS)

    col1, col2 = st.columns([1, 2])

    with col1:
        fig = plot_choropleth(region_df, gdf, keyword, save=False)
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader(f'Regional breakdown — "{keyword}"')
        kw_df = (
            region_df[region_df["keyword"] == keyword]
            .groupby("region")["interest"]
            .mean()
            .reset_index()
            .sort_values("interest", ascending=False)
            .rename(columns={"interest": "avg interest (0–100)"})
        )
        kw_df["avg interest (0–100)"] = kw_df["avg interest (0–100)"].round(1)

        st.dataframe(kw_df, use_container_width=True, hide_index=True)

        top_nation = kw_df.iloc[0]["region"]
        top_score = kw_df.iloc[0]["avg interest (0–100)"]
        st.info(
            f"**{top_nation}** has the highest average search interest "
            f"for '{keyword}' at **{top_score}**."
        )


# ═══════════════════════════════════════════════════════════════════
# PAGE 3 — Time Series
# ═══════════════════════════════════════════════════════════════════
elif page == "Time Series":
    st.title("📈 Time Series")
    st.markdown("Explore how search interest has changed over 5 years.")

    tab1, tab2 = st.tabs(["By category", "By keyword"])

    with tab1:
        category = st.selectbox(
            "Category",
            CATEGORIES,
            format_func=lambda x: x.replace("_", " ").title(),
        )
        fig = plot_time_series(time_df, category, save=False)
        st.pyplot(fig)
        plt.close()

    with tab2:
        keyword = st.selectbox("Keyword", ALL_KEYWORDS, key="ts_keyword")
        kw_df = time_df[time_df["keyword"] == keyword].copy()

        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(kw_df["date"], kw_df["interest"], color="#1f77b4", linewidth=1.5)
        ax.set_title(f'Search interest over time — "{keyword}"', fontweight="bold")
        ax.set_ylabel("Interest (0–100)")
        ax.set_xlabel("Date")
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        # Summary stats
        st.subheader("Summary statistics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Average", round(kw_df["interest"].mean(), 1))
        col2.metric("Peak", round(kw_df["interest"].max(), 1))
        col3.metric(
            "Peak date",
            kw_df.loc[kw_df["interest"].idxmax(), "date"].strftime("%b %Y"),
        )
        col4.metric("Min", round(kw_df["interest"].min(), 1))


# ═══════════════════════════════════════════════════════════════════
# PAGE 4 — Seasonal Analysis
# ═══════════════════════════════════════════════════════════════════
elif page == "Seasonal Analysis":
    st.title("🔄 Seasonal Analysis")
    st.markdown(
        """
        Seasonal decomposition splits a time series into three components:
        **trend** (long-term direction), **seasonal** (repeating yearly pattern),
        and **residual** (unexplained noise or anomalies).
        """
    )

    tab1, tab2 = st.tabs(["Summary", "Individual keyword"])

    with tab1:
        st.subheader("Seasonal patterns by week of year")
        fig = plot_seasonal_summary(time_df, save=False)
        st.pyplot(fig)
        plt.close()

    with tab2:
        seasonal_keywords = [
            "Wimbledon", "Premier League", "Six Nations",
            "cost of living", "mental health", "GP appointment",
        ]
        keyword = st.selectbox("Keyword", seasonal_keywords)
        decomp = decompose_keyword(time_df, keyword)
        if decomp:
            fig = plot_decomposition(decomp, save=False)
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("Not enough data to decompose this keyword.")