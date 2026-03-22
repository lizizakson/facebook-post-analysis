# Behavioral Analysis of Social Media Engagement

A computational behavioral research project studying **what linguistic, emotional, and contextual features drive human engagement** with social media content — and what this reveals about how people respond to language at scale.

The dataset is Facebook posts published by a single author (a behavioral neuroscientist and novelist) over a 9-month period, combined with full engagement metrics from the Facebook analytics dashboard. The personal nature of the data is intentional: it allows precise ground-truth labeling of content features that would be impossible to obtain from anonymous datasets.

---

## Research Questions

1. Do linguistic features — emotional tone, personal disclosure, narrative style — predict audience engagement independently of algorithmic reach?
2. How does the *type* of content (reflective, recommendation, occasion-anchored, book-related) affect engagement patterns?
3. What is the relationship between algorithmic distribution (impressions) and genuine audience resonance (engagement rate) — and what content features drive one versus the other?
4. *(Planned)* How do visual features of accompanying images interact with text features to shape engagement?

These questions sit at the intersection of computational social science, behavioral psychology, and language analysis — combining statistical modeling, LLM-based annotation (Claude via Anthropic API), and classical ML — with longer-term relevance to understanding how linguistic and emotional features shape human responses to generated content more broadly.

---

## Methods

**Data pipeline:**
- Raw export from Facebook analytics dashboard (~100 posts, 9-month window)
- Timezone correction, missing value analysis, cover photo exclusion (with documented justification)
- Feature engineering: engagement rate, repeat view rate, view-through rate, 4-quadrant performance classification

**Exploratory analysis:**
- Engagement metric distributions and correlations
- Post type analysis (Photo / Content / Reel)
- Timing effects (hour of day, day of week)
- Text length analysis
- OLS regression: effect of timing and post type on log(views) and engagement rate

**Text analysis (in progress):**
- LLM-based annotation of linguistic features per post using the Anthropic API
- Dimensions: emotional valence, emotional intensity, tone category, marketing mention, occasion relevance
- Each score accompanied by a brief model-generated explanation for interpretability

**Modeling (planned):**
- Predictive model (logistic regression / random forest) for post performance category
- Feature importance analysis to identify which behavioral/linguistic features matter most

---

## Structure

```
data/
  010625_190326_fb_posts.csv     # raw export from Facebook analytics
  clean_posts.csv                # cleaned, feature-engineered dataset (output of 01_clean)

notebooks/
  01_clean.ipynb                 # data cleaning, timezone correction, feature engineering, export
  02_eda.ipynb                   # exploratory analysis and visualisation
  03_text_analysis.ipynb         # LLM-based linguistic annotation (in progress)
  04_modeling.ipynb              # predictive modeling (planned)
```

---

## Key Design Decisions

**Why personal data?**
Using one author's posts allows precise content labeling — tone, intent, occasion context — that cannot be reliably inferred from anonymous data. It also enables a natural experiment: the author's writing style is consistent, so variance in engagement is more attributable to content features than to author differences.

**Why exclude cover photo changes?**
Cover photo changes generate engagement through Facebook's automatic follower notification system, not through organic feed distribution. Including them would conflate two fundamentally different engagement mechanics and bias any model trying to learn what makes *written content* resonate.

**Why a 4-quadrant classification?**
Separating algorithmic reach (impressions) from audience resonance (engagement rate) captures a distinction that aggregate metrics miss — a post can succeed algorithmically without resonating with its audience, and vice versa. The quadrant framework makes this distinction explicit and actionable.

---

## Tools

- Python, Pandas, NumPy
- Seaborn, Matplotlib
- Statsmodels
- Anthropic API (Claude) for text annotation
- Jupyter Notebooks

---

## Author

**Liz Izakson Mashal** — Behavioral neuroscientist (PhD, Tel Aviv University) with research experience in cognitive biases, human-computer interaction, and human-centered AI evaluation. This project is part of an ongoing effort to apply behavioral research methods to questions about human engagement with language — with direct relevance to alignment research on how humans respond to and are influenced by AI-generated content.
