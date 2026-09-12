# Movie &amp; TV Show Recommendation Model

A content-based recommendation system that suggests similar movies and TV shows from a
Netflix catalogue of **8,807 titles**, using TF-IDF vectorisation and cosine similarity over
each title's **name, description, and genre**.

The application is a single-process [Streamlit](https://streamlit.io/) web app. A user picks
one of 20 curated titles, reviews the 10 closest matches one at a time, rates each one
(*Yes / Maybe / No*), and is then shown how relevant the model's suggestions were — plus a
descriptive breakdown of the underlying catalogue.

---

## Contents

| Document | What it covers |
| --- | --- |
| **README.md** (this file) | Overview, quickstart, project layout |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, routing, data flow, module boundaries, design decisions |
| [docs/MODEL.md](docs/MODEL.md) | The recommendation algorithm, feature engineering, complexity, evaluation, limitations |
| [docs/DATA.md](docs/DATA.md) | Dataset schema, provenance, profile, quality notes, licensing |
| [docs/ENGINEERING.md](docs/ENGINEERING.md) | Dev environment, code map, conventions, testing strategy, known issues |
| [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md) | Runtime requirements, resource footprint, deployment, operations runbook |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to propose and land changes |
| [CHANGELOG.md](CHANGELOG.md) | Release history |

---

## Quickstart

### Prerequisites

- **Python 3.12** or newer (3.12 and 3.13 are both fine)
- **Streamlit 1.52.0 or newer** — this is a hard requirement, see
  [the version note below](#streamlit-version-requirement)
- ~1.5 GB of free RAM per concurrent user (see
  [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md#3-resource-footprint))

### Install and run

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead.

```bash
pip install -r requirements.txt
```

```bash
streamlit run main.py
```

Streamlit prints a local URL (by default <http://localhost:8501>) and opens it in your
browser.

### Using the app

1. **Selection page** — click any of the 20 title cards.
2. **About Media** — read the details for your pick, then click **Get Recommendations!**
3. **Recommendations** — you are shown 10 similar titles, one per screen. Answer
   **Yes**, **Maybe**, or **No** for each.
4. **Model Analysis** — see the relevance score derived from your answers, a bar chart of
   your response mix, and a list of every answer you gave. Click
   **Get Descriptive Analysis**.
5. **Descriptive Analysis** — a treemap of the 10 most common genres in the catalogue and a
   pie chart of the top 5.

> The app has no "back" navigation. To start over with a different title, refresh the
> browser page. See [docs/ENGINEERING.md](docs/ENGINEERING.md#5-known-issues-and-technical-debt).

### Streamlit version requirement

`media_selection.py` calls `st.container(border=False, width="content")`. The `width`
parameter did not exist on `st.container` before Streamlit **1.48.0**, and the literal value
`"content"` was rejected by Streamlit's own runtime validation until **1.52.0**. On anything
older the selection page raises an exception on first render.

| Streamlit version | Result |
| --- | --- |
| `< 1.48.0` | `TypeError` — `container()` got an unexpected keyword argument `width` |
| `1.48.0` – `1.51.x` | `StreamlitInvalidWidthError` — `"content"` is not an accepted width |
| `>= 1.52.0` | Works |

`requirements.txt` pins this floor. The unpinned `pip install streamlit` in older setup
instructions happens to work today only because the current release is well past 1.52.

---

## Project layout

```
RecommendationModel/
├── main.py                       # Entry point: loads data, owns routing
├── recommendation_model.py       # The ML model (TF-IDF + cosine similarity)
├── media_selection.py            # Page 1: pick a title
├── about_selected_media.py       # Page 2: details for the picked title
├── media_recommendations.py      # Page 3: rate 10 recommendations
├── model_analysis.py             # Page 4: relevance score + response breakdown
├── descriptive_analysis.py       # Page 5: catalogue treemap + pie chart
├── css/                          # One style module per page
│   ├── media_selection_css.py
│   ├── about_media_css.py
│   ├── media_recommendations_css.py
│   ├── model_analysis_css.py
│   └── descriptive_analysis_css.py
├── dataset/
│   └── movies_and_tv_shows_dataset.csv   # 8,807 titles (Title, Genre, Description)
├── mediaImages/                  # 21 PNG posters (~18 MB) for the selection page
├── docs/                         # Architecture, model, data, engineering, infra docs
├── requirements.txt
├── CONTRIBUTING.md
└── CHANGELOG.md
```

---

## How it works, in one paragraph

Every title's `Title`, `Description`, and `Genre` are concatenated into a single text field.
That corpus is converted to a TF-IDF matrix (English stop words removed), and a full
pairwise **cosine similarity matrix** is computed across all 8,807 titles. To make
recommendations for a selected title, the model reads that title's row of the matrix, sorts
descending, drops the top entry (the title itself), and returns the next 10. The user's
Yes/Maybe/No answers are scored 1 / 0.5 / 0 and averaged over 10 to produce the relevance
percentage. Full detail in [docs/MODEL.md](docs/MODEL.md).

---

## Technology

| Layer | Choice |
| --- | --- |
| Language | Python 3.12+ |
| UI / server | Streamlit |
| Data handling | pandas |
| ML | scikit-learn (`TfidfVectorizer`, `cosine_similarity`) |
| Charts | matplotlib, seaborn, squarify, Streamlit's built-in `st.bar_chart` |
| Storage | A single CSV file — no database |

---

## Data source

- **Platform:** [Kaggle](https://www.kaggle.com/)
- **Dataset:** [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)
- **Local copy:** `dataset/movies_and_tv_shows_dataset.csv`, reduced to three columns

See [docs/DATA.md](docs/DATA.md) for the full schema, profile, and licensing notes.

---

## Original development environment

Recorded for reproducibility. The project is not tied to this hardware or OS.

- **Device:** iMac, Intel Core i5, 8 GB 2400 MHz DDR4
- **OS:** macOS Ventura 13.7.8
- **IDE:** PyCharm 2024.1.4 (Professional Edition)
- **Python:** 3.12

---

## Status and limitations

This is a demonstration / portfolio project. Before treating it as production software,
read [docs/ENGINEERING.md](docs/ENGINEERING.md#5-known-issues-and-technical-debt) — in
particular the recommendation model is recomputed from scratch on every interaction, and the
page styling is pinned to Streamlit's internal, unstable CSS class names.
