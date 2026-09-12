# Changelog

All notable changes to this project are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project does
not yet use version tags; the `0.1.0` entry below reconstructs the initial delivery from the
commit history.

---

## [Unreleased]

### Added

- Documentation set:
  - [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design, module map, routing,
    data flow, design decisions, quality attributes, and a target architecture
  - [`docs/MODEL.md`](docs/MODEL.md) — the recommendation algorithm, feature engineering,
    vectorisation parameters, computational cost, relevance scoring, and limitations
  - [`docs/DATA.md`](docs/DATA.md) — dataset provenance, schema, profile, poster assets,
    a catalogue refresh procedure, and licensing notes
  - [`docs/ENGINEERING.md`](docs/ENGINEERING.md) — dev environment, code map, conventions,
    a five-tier testing strategy, eleven catalogued issues, and security considerations
  - [`docs/INFRASTRUCTURE.md`](docs/INFRASTRUCTURE.md) — runtime topology, resource
    footprint, deployment options, rollback, observability, and an operations runbook
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — setup, pre-change checklist, conventions, and a
  scoped list of good first contributions
- [`requirements.txt`](requirements.txt) — declares the six runtime dependencies, replacing
  the loose `pip install` list that previously lived only in the README
- This changelog

### Changed

- [`README.md`](README.md) rewritten: adds a documentation index, project layout, an
  explanation of how the model works, and the Streamlit version requirement. Retains the
  original development-environment and data-source sections

### Documented (no code change)

The following were discovered while writing the documentation and are recorded rather than
fixed. Each is described in
[docs/ENGINEERING.md](docs/ENGINEERING.md#5-known-issues-and-technical-debt).

- **Streamlit 1.52.0 is a hard minimum.** `media_selection.py` passes `width="content"` to
  `st.container()`. Streamlit's runtime validation rejected that value before 1.52.0, and the
  parameter did not exist at all before 1.48.0 — so the app's entry page fails on first render
  against anything older. This was previously undocumented and unconstrained
- The recommendation model rebuilds a 620 MB dense similarity matrix on every user
  interaction — 11+ times per session — to read a single row of it
- The page styling targets Streamlit-generated Emotion CSS class hashes, which change between
  releases and break the layout silently
- `recommendation_model.py` mutates the DataFrame passed to it
- `model_analysis.py` carries an unused cross-page import of `recommendationModel`
- The recommendation count `10` is hard-coded independently in two modules; changing one
  without the other silently corrupts the reported relevance score
- Navigation is forward-only, and the Descriptive Analysis page is a dead end
- `mediaImages/movie_temp.png` is referenced by no source file

---

## [0.1.0] — 2026-03-26

Initial delivery. Reconstructed from commits and pull requests #1–#5 in
[Dcorl/RecommendationModel](https://github.com/Dcorl/RecommendationModel).

### Added

- **Dataset import** — the Netflix Movies and TV Shows catalogue from Kaggle, reduced to
  `Title`, `Genre`, and `Description` (8,807 rows)
- **Media selection page** (PR #1) — a four-column grid of 20 curated movie and TV show
  cards with local poster artwork, plus per-page CSS
- **About Selected Media page** (PR #2) — title, genre, and description for the user's
  selection alongside its poster
- **Recommendation model** — TF-IDF vectorisation of a combined title + description + genre
  text field, with cosine similarity ranking to return the 10 closest titles
- **Recommendations page** (PR #3) — presents the 10 results one at a time and records a
  Yes / Maybe / No rating for each
- **Model Analysis page** (PR #4) — converts the ratings (1 / 0.5 / 0) into a relevance
  percentage, with a response bar chart and a full list of answers
- **Descriptive Analysis page** (PR #5) — a squarify treemap of the 10 most common genres
  and a matplotlib pie chart of the top 5
- **Session-state routing** in `main.py` driving a forward-only five-page flow
- **Per-page CSS modules** under `css/`, one per page
- **README** with the development environment, library list, data source, and run
  instructions
