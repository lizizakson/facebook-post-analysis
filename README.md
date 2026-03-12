# Facebook Post Performance Analysis

Exploratory analysis of Facebook post performance for **Liz Izakson Mashal**, using data exported from Meta Business Suite.

## Goals

Understand what influences post performance:

- posting time (hour of day, day of week)
- post type (Photo, Content, Reel, Link)
- audience engagement vs algorithmic exposure
- views and viewer behaviour

## Data

- Source: Meta Business Suite export (`data/010625_120326_fb_posts.csv`)
- Clean version (Liz's posts only, correct timestamps): `data/facebook_posts_clean.csv`
- Posts are filtered to **Liz's own page only** — tagged posts from other pages are excluded from analysis
- Timezone correction applied: +10h for posts before 2026-03-08, +9h from 2026-03-08 onwards

## Methods

- Data cleaning and column normalisation
- Post origin classification (My Post vs Tagged) using `page_name`
- Missing value analysis — structural missingness identified and documented
- Feature engineering:
  - Engagement rate (`interactions / impressions`)
  - Repeat view rate (`views / unique viewers`)
  - View-through rate (`unique viewers / impressions`)
  - Post category classification (Viral / Audience Favorite / Algorithm Pushed / Low Performance)
- Exploratory data analysis and visualisation
- OLS regression: effect of hour, day of week, and post type on `log(views+1)` and `engagement_rate`

## Tools

- Python, Pandas, NumPy
- Seaborn, Matplotlib, Plotly
- Statsmodels (OLS regression)
- Jupyter Notebook

## Structure

```
data/
  010625_120326_fb_posts.csv   # raw export from Meta
  facebook_posts_clean.csv     # cleaned, filtered, corrected timestamps

notebooks/
  facebook_analysis_clean.ipynb  # main analysis notebook (organised, with explanations)
  facebook_analysis.ipynb        # original unorganised notebook

code/
  dashboard.py    # generates interactive HTML dashboard
  dashboard.html  # output dashboard (open in browser)
```

## Running the Dashboard

```bash
python code/dashboard.py
```

Generates `code/dashboard.html` and exports `data/facebook_posts_clean.csv`.
