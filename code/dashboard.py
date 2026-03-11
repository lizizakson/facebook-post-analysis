"""
Facebook Post Performance Dashboard
=====================================
Generates an interactive HTML dashboard summarising engagement patterns
from the facebook_posts.csv dataset.

Usage:
    python dashboard.py
    # Opens dashboard.html in the current directory (or ./output/ if it exists)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── 1. Load & clean data ─────────────────────────────────────────────────────

DATA_PATH = Path(__file__).parent.parent / "data" / "facebook_posts.csv"
df = pd.read_csv(DATA_PATH)

# Normalise column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(r"[^\w]+", "_", regex=True)
)

# Ensure numeric types
numeric_cols = [
    "views", "comments", "impressions", "interactions",
    "reactions", "saves", "shares", "viewers",
    "average_seconds_viewed", "seconds_viewed",
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Parse timestamps and apply the known +10 h offset correction
df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce") + pd.Timedelta(hours=10)
df["date"]    = df["publish_time"].dt.date
df["hour"]    = df["publish_time"].dt.hour
df["weekday"] = df["publish_time"].dt.day_name()

# Classify post origin based on page_name:
# - "My Post": posted on Liz's own page
# - "Tagged": appeared on her page because someone else tagged her
df["post_origin"] = df["page_name"].apply(
    lambda x: "My Post" if x == "Liz Izakson Mashal" else "Tagged"
)

# Separate tagged posts — they originate from other pages and skew the analysis
df_tagged = df[df["post_origin"] == "Tagged"].copy()
df = df[df["post_origin"] == "My Post"].copy()

# Derived metrics
df["engagement_rate"] = df["interactions"] / df["impressions"].replace(0, np.nan)

# Post classification (quadrant: impressions vs engagement_rate)
imp_med = df["impressions"].median()
eng_med = df["engagement_rate"].median()

def classify_post(row):
    high_imp = row["impressions"] >= imp_med
    high_eng = row["engagement_rate"] >= eng_med
    if high_imp and high_eng:
        return "Viral"
    elif not high_imp and high_eng:
        return "Audience Favorite"
    elif high_imp and not high_eng:
        return "Algorithm Pushed"
    else:
        return "Low Performance"

df["post_category"] = df.apply(classify_post, axis=1)

# Truncate title for display
df["title_short"] = df["title"].str.slice(0, 80).str.replace(r"\n", " ", regex=True) + "…"

CATEGORY_COLORS = {
    "Viral":             "#2ecc71",
    "Audience Favorite": "#3498db",
    "Algorithm Pushed":  "#e67e22",
    "Low Performance":   "#bdc3c7",
}
WEEKDAY_ORDER = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# ── 2. Build dashboard ───────────────────────────────────────────────────────

fig = make_subplots(
    rows=4, cols=3,
    subplot_titles=[
        "Post Type Distribution",
        "Avg Engagement Rate by Post Type",
        "Avg Impressions by Post Type",
        "Engagement Rate Distribution",
        "Interactions vs Impressions",
        "Post Category Breakdown",
        "Avg Engagement Rate by Hour",
        "Avg Impressions by Hour",
        "Post Category by Post Type",
        "Avg Engagement Rate by Day of Week",
        "Avg Impressions by Day of Week",
        "Top 10 Posts by Engagement Rate",
    ],
    specs=[
        [{"type": "pie"},   {"type": "bar"}, {"type": "bar"}],
        [{"type": "histogram"}, {"type": "scatter"}, {"type": "bar"}],
        [{"type": "bar"},   {"type": "bar"}, {"type": "bar"}],
        [{"type": "bar"},   {"type": "bar"}, {"type": "table"}],
    ],
    vertical_spacing=0.12,
    horizontal_spacing=0.08,
)

# ── Row 1: Post type overview ─────────────────────────────────────────────

# 1a. Post type distribution (pie)
type_counts = df["post_type"].value_counts()
fig.add_trace(
    go.Pie(
        labels=type_counts.index,
        values=type_counts.values,
        hole=0.4,
        textinfo="percent+label",
        showlegend=False,
    ),
    row=1, col=1,
)

# 1b. Avg engagement rate by post type
type_eng = df.groupby("post_type")["engagement_rate"].mean().sort_values(ascending=False)
fig.add_trace(
    go.Bar(
        x=type_eng.index,
        y=type_eng.values,
        marker_color=px.colors.qualitative.Pastel[:len(type_eng)],
        showlegend=False,
        text=[f"{v:.3f}" for v in type_eng.values],
        textposition="outside",
    ),
    row=1, col=2,
)

# 1c. Avg impressions by post type
type_imp = df.groupby("post_type")["impressions"].mean().sort_values(ascending=False)
fig.add_trace(
    go.Bar(
        x=type_imp.index,
        y=type_imp.values,
        marker_color=px.colors.qualitative.Pastel[:len(type_imp)],
        showlegend=False,
        text=[f"{v:.0f}" for v in type_imp.values],
        textposition="outside",
    ),
    row=1, col=3,
)

# ── Row 2: Engagement rate & scatter ─────────────────────────────────────

# 2a. Engagement rate histogram
fig.add_trace(
    go.Histogram(
        x=df["engagement_rate"].dropna(),
        nbinsx=25,
        marker_color="#3498db",
        opacity=0.8,
        showlegend=False,
    ),
    row=2, col=1,
)

# 2b. Impressions vs interactions scatter coloured by category
for cat, color in CATEGORY_COLORS.items():
    mask = df["post_category"] == cat
    sub = df[mask]
    fig.add_trace(
        go.Scatter(
            x=sub["impressions"],
            y=sub["interactions"],
            mode="markers",
            name=cat,
            marker=dict(color=color, size=8, opacity=0.8, line=dict(width=0.5, color="white")),
            text=sub["title_short"],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Impressions: %{x:,}<br>"
                "Interactions: %{y}<br>"
                "<extra></extra>"
            ),
        ),
        row=2, col=2,
    )

# Quadrant reference lines (drawn as scatter traces to avoid pie-chart subplot conflicts)
imp_range = [df["impressions"].min(), df["impressions"].max()]
int_median = df["interactions"].median()
imp_median = df["impressions"].median()
int_range = [df["interactions"].min(), df["interactions"].max()]

fig.add_trace(
    go.Scatter(
        x=imp_range, y=[int_median, int_median],
        mode="lines", line=dict(dash="dot", color="grey", width=1),
        showlegend=False, hoverinfo="skip",
    ),
    row=2, col=2,
)
fig.add_trace(
    go.Scatter(
        x=[imp_median, imp_median], y=int_range,
        mode="lines", line=dict(dash="dot", color="grey", width=1),
        showlegend=False, hoverinfo="skip",
    ),
    row=2, col=2,
)

# 2c. Post category breakdown (horizontal bar)
cat_counts = df["post_category"].value_counts()
fig.add_trace(
    go.Bar(
        x=cat_counts.values,
        y=cat_counts.index,
        orientation="h",
        marker_color=[CATEGORY_COLORS.get(c, "#aaa") for c in cat_counts.index],
        showlegend=False,
        text=cat_counts.values,
        textposition="outside",
    ),
    row=2, col=3,
)

# ── Row 3: Time-of-day patterns ───────────────────────────────────────────

hourly = df.groupby("hour")[["engagement_rate", "impressions"]].mean()

# 3a. Engagement rate by hour
fig.add_trace(
    go.Bar(
        x=hourly.index,
        y=hourly["engagement_rate"],
        marker_color="#9b59b6",
        showlegend=False,
    ),
    row=3, col=1,
)

# 3b. Impressions by hour
fig.add_trace(
    go.Bar(
        x=hourly.index,
        y=hourly["impressions"],
        marker_color="#1abc9c",
        showlegend=False,
    ),
    row=3, col=2,
)

# 3c. Category by post type (stacked bar)
cat_type = pd.crosstab(df["post_type"], df["post_category"])
for cat in CATEGORY_COLORS:
    if cat in cat_type.columns:
        fig.add_trace(
            go.Bar(
                name=cat,
                x=cat_type.index,
                y=cat_type[cat],
                marker_color=CATEGORY_COLORS[cat],
                showlegend=True,
            ),
            row=3, col=3,
        )

# ── Row 4: Day-of-week & top posts ───────────────────────────────────────

weekday_perf = (
    df.groupby("weekday")[["engagement_rate", "impressions"]]
    .mean()
    .reindex(WEEKDAY_ORDER)
    .dropna(how="all")
)

# 4a. Engagement rate by weekday
fig.add_trace(
    go.Bar(
        x=weekday_perf.index,
        y=weekday_perf["engagement_rate"],
        marker_color="#e74c3c",
        showlegend=False,
    ),
    row=4, col=1,
)

# 4b. Impressions by weekday
fig.add_trace(
    go.Bar(
        x=weekday_perf.index,
        y=weekday_perf["impressions"],
        marker_color="#f39c12",
        showlegend=False,
    ),
    row=4, col=2,
)

# 4c. Top-10 posts table
top10 = (
    df.dropna(subset=["engagement_rate"])
    .sort_values("engagement_rate", ascending=False)
    .head(10)[["title_short", "post_type", "post_category", "impressions", "interactions", "engagement_rate"]]
)
fig.add_trace(
    go.Table(
        header=dict(
            values=["Title", "Type", "Category", "Impressions", "Interactions", "Eng. Rate"],
            fill_color="#2c3e50",
            font=dict(color="white", size=11),
            align="left",
        ),
        cells=dict(
            values=[
                top10["title_short"],
                top10["post_type"],
                top10["post_category"],
                top10["impressions"].map("{:,.0f}".format),
                top10["interactions"].map("{:.0f}".format),
                top10["engagement_rate"].map("{:.3f}".format),
            ],
            fill_color=[
                ["#ecf0f1" if i % 2 == 0 else "white" for i in range(len(top10))]
            ],
            font=dict(size=10),
            align="left",
        ),
    ),
    row=4, col=3,
)

# ── 3. Layout & axis labels ───────────────────────────────────────────────

fig.update_layout(
    title=dict(
        text="<b>Facebook Post Performance Dashboard</b>",
        font=dict(size=22),
        x=0.5,
    ),
    height=1600,
    barmode="stack",   # applies to stacked bar in row 3 col 3
    legend=dict(
        title="Post Category",
        orientation="v",
        x=1.01,
        y=0.35,
    ),
    paper_bgcolor="white",
    plot_bgcolor="#f9f9f9",
    font=dict(family="Arial, sans-serif", size=12),
)

# Axis labels
fig.update_xaxes(title_text="Post Type",       row=1, col=2)
fig.update_yaxes(title_text="Avg Eng. Rate",   row=1, col=2)
fig.update_xaxes(title_text="Post Type",       row=1, col=3)
fig.update_yaxes(title_text="Avg Impressions", row=1, col=3)

fig.update_xaxes(title_text="Engagement Rate", row=2, col=1)
fig.update_yaxes(title_text="Count",           row=2, col=1)
fig.update_xaxes(title_text="Impressions",     row=2, col=2)
fig.update_yaxes(title_text="Interactions",    row=2, col=2)
fig.update_xaxes(title_text="Count",           row=2, col=3)

fig.update_xaxes(title_text="Hour of Day",     row=3, col=1)
fig.update_xaxes(title_text="Hour of Day",     row=3, col=2)
fig.update_xaxes(title_text="Post Type",       row=3, col=3)

fig.update_xaxes(title_text="Day of Week",     row=4, col=1)
fig.update_xaxes(title_text="Day of Week",     row=4, col=2)

# ── 4. Save output ────────────────────────────────────────────────────────

output_path = Path(__file__).parent / "dashboard.html"
fig.write_html(str(output_path), include_plotlyjs="cdn")
print(f"Dashboard saved to: {output_path.resolve()}")

# Try to open automatically
import webbrowser
webbrowser.open(output_path.resolve().as_uri())
