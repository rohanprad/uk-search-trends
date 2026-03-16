# 🇬🇧 UK Google Search Trends Analysis

An analysis of regional Google search interest across the UK using the Google Trends API.
Inspired by V1 Analytics' US-focused work, this project maps search behaviour by UK region and city.

## What this project covers
- Geographic breakdown of search interest by UK region and city
- Topic and keyword discovery — what are different parts of the UK searching for?
- Interactive Streamlit dashboard for exploration

## Data source
Google Trends via the `pytrends` unofficial API.

## Setup
```bash
git clone https://github.com/rohanprad/uk-search-trends.git
cd uk-search-trends
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python src/collect.py
streamlit run app/dashboard.py
```

## Project structure
uk-search-trends/
├── data/
│   ├── raw/          # unmodified CSVs from pytrends
│   └── processed/    # cleaned data ready for analysis
├── notebooks/        # exploratory work (optional scratch pad)
├── src/
│   ├── collect.py    # data collection via pytrends
│   ├── clean.py      # data cleaning and processing
│   ├── analyse.py    # analysis functions
│   └── visualise.py  # chart/map helpers
├── app/
│   └── dashboard.py  # Streamlit app
├── assets/           # shapefiles, images, logos
├── requirements.txt
├── .gitignore
└── README.md

## Methodology
[to be completed]

## Key findings
[to be completed]