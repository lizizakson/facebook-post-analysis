# Project Setup Guide

This guide explains how to set up the development environment and run the analysis notebooks.
Written for macOS. If you're coming back to this project after a break — start at **Step 3**.

---

## Getting Your Data from Facebook

Before running any notebooks, you need to export your post analytics from Facebook.
This requires a **professional profile** (creator or business mode) — standard personal
profiles do not have access to the analytics dashboard.

### Step 0 — Enable Professional Mode on your Facebook profile

If you haven't already:

1. Go to your Facebook profile
2. Click the three dots (···) below your cover photo
3. Select **Turn on professional mode**
4. Follow the prompts — choose **Creator** as your profile type

You only need to do this once. Professional mode unlocks the analytics dashboard
and gives you access to post-level metrics (impressions, interactions, reach, etc.).

### Exporting your data

1. Go to your Facebook **profile** (not a page — your personal profile in creator mode)
2. Click **Professional dashboard** — usually visible below your bio
3. In the dashboard, navigate to **Posts** or **Content** analytics
4. Look for an **Export** option (usually top right)
5. Select **CSV** as the format
6. **Choose your date range carefully** — start from the date you became consistently
   active (at least one post per week). Including periods of low activity introduces
   noise since posting frequency affects the Facebook algorithm and therefore engagement.
7. Download the CSV and place it in the `data/` folder of this project

### Known data issues to be aware of

- **Timezone offset** — Facebook exports timestamps in a UTC offset that does not
  match your actual local posting time. `01_clean.ipynb` corrects for this automatically,
  but the offset has changed between export batches. Always verify the corrected
  timestamps in the timezone verification cell before proceeding.
- **Missing metrics** — Posts that are too recent (less than ~48 hours old) may have
  incomplete metrics. `01_clean.ipynb` detects and removes these automatically.
- **Tagged posts** — Posts where other people tagged you appear in the export but
  have incomplete metrics. These are automatically separated and excluded from analysis.
- **Cover photo changes** — Facebook includes cover photo updates as "posts" in the
  export. These are excluded because they have no text content and are promoted via
  a different algorithmic mechanism (automatic follower notifications).

---

## Project Structure

```
facebook_analysis/
├── .env                        # API keys (not tracked by Git)
├── .gitignore
├── README.md                   # Project overview and research questions
├── SETUP.md                    # This file
├── data/
│   ├── 010625_190326_fb_posts.csv      # Raw Facebook analytics export
│   ├── clean_posts.csv                 # Cleaned dataset (output of 01_clean)
│   └── clean_posts_with_text.csv       # Enriched dataset (output of 03_text_analysis)
└── notebooks/
    ├── 01_clean.ipynb           # Data cleaning & feature engineering
    ├── 02_eda.ipynb             # Exploratory data analysis (behavioral features)
    ├── 04_eda_text.ipynb        # Text feature EDA & annotation quality
    ├── 03_text_analysis.ipynb   # LLM-based annotation via Anthropic API
    └── 04_modeling.ipynb        # Predictive modeling (planned)
```

---

## Requirements

- **macOS** (instructions are Mac-specific)
- **Python 3.13.7**
- **VS Code** — download from [code.visualstudio.com](https://code.visualstudio.com)
- An **Anthropic API key** — required only for `03_text_analysis.ipynb`

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/lizizakson/facebook-post-analysis.git
cd facebook_analysis
```

---

## Step 2 — Create the Virtual Environment

A virtual environment keeps project dependencies isolated from your system Python.
You only need to do this once.

```bash
python3 -m venv .venv
```

---

## Step 3 — Activate the Virtual Environment

**You must do this every time you open a new terminal session.**

```bash
source .venv/bin/activate
```

You'll know it worked when you see `(.venv)` at the start of your terminal prompt:

```
(.venv) your-name@your-machine facebook_analysis %
```

To deactivate when you're done:

```bash
deactivate
```

---

## Step 4 — Install Dependencies

Only needed once (or after adding new packages):

```bash
pip install pandas numpy matplotlib seaborn statsmodels \
            anthropic python-dotenv jupyter ipython
```

### Installed package versions (verified working)

| Package | Version |
|---|---|
| pandas | 3.0.1 |
| anthropic | 0.86.0 |
| python-dotenv | 1.2.2 |
| seaborn | 0.13.2 |
| statsmodels | 0.14.6 |

---

## Step 5 — Set Up the Anthropic API Key

Required only for `03_text_analysis.ipynb`. Skip if you're only running the other notebooks.

1. Get an API key at [console.anthropic.com](https://console.anthropic.com)
2. Create a `.env` file in the project root:

```bash
touch .env
```

3. Open `.env` and add your key:

```
ANTHROPIC_API_KEY=your-key-here
```

4. Verify `.env` is in `.gitignore` (it should be — never commit API keys to Git):

```bash
cat .gitignore | grep .env
```

---

## Step 6 — Open VS Code

Open VS Code from the project folder:

```bash
open -a "Visual Studio Code" .
```

Or open VS Code manually and use **File → Open Folder** to select the project folder.

### Select the correct Python interpreter in VS Code

This tells VS Code to use the project's virtual environment:

1. Press `Cmd + Shift + P`
2. Type `Python: Select Interpreter`
3. Choose the option that contains `.venv` — something like:
   `./venv/bin/python` or `Python 3.13.7 (.venv)`

You only need to do this once per project.

---

## Step 7 — Run the Notebooks

Open any `.ipynb` file from the `notebooks/` folder in VS Code.

### Recommended run order

| Notebook | Input | Output | Notes |
|---|---|---|---|
| `01_clean.ipynb` | Raw CSV | `clean_posts.csv` | Re-run when new Facebook data is added |
| `02_eda.ipynb` | `clean_posts.csv` | — | Behavioral & timing analysis |
| `03_text_analysis.ipynb` | `clean_posts.csv` | `clean_posts_with_text.csv` | Requires API key. Uses checkpoint — safe to interrupt and restart |
| `04_eda_text.ipynb` | `clean_posts_with_text.csv` | — | Run after `03_text_analysis` is complete |
| `05_modeling.ipynb` | `clean_posts_with_text.csv` | — | Planned |
| `04_modeling.ipynb` | `clean_posts_with_text.csv` | — | Planned |

### Restarting the kernel

If a notebook behaves unexpectedly, restart the kernel:
- Click the kernel name (top right of the notebook) → **Restart**
- Then re-run all cells from the top

---

## Common Issues

**`ModuleNotFoundError`**
The virtual environment is not active, or the package isn't installed.
```bash
source .venv/bin/activate
pip install <package-name>
```

**`ANTHROPIC_API_KEY not found`**
The `.env` file is missing or the key isn't set correctly.
Check that `.env` exists in the project root and contains the correct key.

**`FileNotFoundError` for a CSV**
Run the notebooks in order — each notebook produces the CSV that the next one needs.

**Timezone warning in `01_clean.ipynb`**
New posts detected beyond `KNOWN_LATEST`. Update the configuration cell at the top
of `01_clean.ipynb` and verify the corrected timestamps look correct before proceeding.

---

## Adding New Facebook Data

1. Download a new CSV from the Facebook analytics dashboard
2. Update `DATA_FILE` and `KNOWN_LATEST` in the configuration cell of `01_clean.ipynb`
3. Re-run `01_clean.ipynb` — it will detect new posts automatically
4. Re-run `03_text_analysis.ipynb` — the checkpoint system will score only new posts
5. Re-run `02_eda.ipynb` and `02b_text_eda.ipynb` to refresh the analysis
