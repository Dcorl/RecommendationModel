# Engineering Guide

> Scope: how to work on this codebase — environment setup, code map, conventions, how to make
> the common kinds of change, testing, and the outstanding technical debt.
> For system design see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 1. Development environment

### Requirements

| Component | Requirement | Notes |
| --- | --- | --- |
| Python | **3.12+** | 3.12 and 3.13 both verified. Current pandas, scikit-learn, matplotlib all require ≥3.11 |
| Streamlit | **≥ 1.52.0** | Hard requirement — see [the version floor](#the-streamlit-152-floor) |
| RAM | 2 GB free minimum | The model allocates ~620 MB per call; see [INFRASTRUCTURE.md](INFRASTRUCTURE.md#3-resource-footprint) |
| Disk | ~250 MB | ~20 MB project + ~230 MB dependencies |

### Setup

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

Windows PowerShell uses `.venv\Scripts\Activate.ps1`.

```bash
pip install -r requirements.txt
```

```bash
streamlit run main.py
```

### Working on the app

Streamlit watches the source tree. Saving any `.py` file shows a **Rerun / Always rerun**
prompt in the browser; pick *Always rerun* during development so edits apply immediately.

Note that a rerun **does not clear `st.session_state`**. After changing routing or state
logic, hard-refresh the browser tab to get a clean session — otherwise you are testing new
code against stale state.

### The Streamlit 1.52 floor

[`media_selection.py:47`](../media_selection.py:47) calls:

```python
with st.container(border=False, width="content"):
```

The `width` parameter and the specific value `"content"` were introduced at different times:

| Streamlit version | `st.container(width=...)` | `width="content"` | Result on the selection page |
| --- | --- | --- | --- |
| `< 1.48.0` | Not present | — | `TypeError` on first render |
| `1.48.0` – `1.51.x` | Present, typed `WidthWithoutContent` | Rejected by `validate_width(width)` | `StreamlitInvalidWidthError` on first render |
| `>= 1.52.0` | Present | Accepted — `validate_width(width, allow_content=True)` | Works |

`requirements.txt` pins `streamlit>=1.52.0` for this reason. Do not relax it without removing
the `width="content"` call.

### No lockfile

`requirements.txt` uses minimum-version constraints, not pins. Two developers installing on
different days can get different dependency versions. For a reproducible environment, freeze
after a known-good install:

```bash
pip freeze > requirements.lock.txt
```

This matters more than usual here, because the page styling is tied to Streamlit's internal
CSS class names — see [the CSS fragility issue](#1-css-targets-streamlits-internal-class-names).

---

## 2. Code map

```
main.py                      37 lines   Entry point, data load, routing
recommendation_model.py      30 lines   TF-IDF + cosine similarity
media_selection.py           56 lines   Page 1 — 20-card picker
about_selected_media.py      30 lines   Page 2 — title detail
media_recommendations.py     68 lines   Page 3 — rate 10 recommendations
model_analysis.py            50 lines   Page 4 — relevance score
descriptive_analysis.py      48 lines   Page 5 — catalogue charts
css/media_selection_css.py   48 lines
css/about_media_css.py       43 lines
css/model_analysis_css.py    38 lines
css/media_recommendations_css.py  36 lines
css/descriptive_analysis_css.py    8 lines  (empty rule set)
                            ---------
                            ~563 lines total
```

### Reading order for a newcomer

1. [`main.py`](../main.py) — the whole routing model fits on one screen.
2. [`recommendation_model.py`](../recommendation_model.py) — the entire ML surface, 30 lines.
3. [`media_selection.py`](../media_selection.py) — how state gets written and a transition
   fires.
4. [`media_recommendations.py`](../media_recommendations.py) — the most complex page; the
   state machine that walks 10 recommendations.

---

## 3. Conventions

These are the conventions the existing code follows. Match them, or change them everywhere
at once.

| Convention | Current practice |
| --- | --- |
| Page entry points | One `render<PageName>Page(...)` function per module, `lowerCamelCase` |
| Module names | `snake_case`, named after the page they render |
| Style functions | One per page in `css/`, no arguments, named after the page |
| CSS gating | Every page wraps its style call in `if page == "<Page Name>":` |
| Page identifiers | Human-readable strings (`"About Media"`, `"Model Analysis"`) used as both route keys and CSS gates |
| Transitions | Set `st.session_state.page`, then call `st.rerun()` — always in that order |
| Comments | Dense inline `#` comments explaining intent |
| Type hints | None used |
| Docstrings | None used |

### Naming inconsistency to be aware of

Function names are `lowerCamelCase` (`renderSelectionPage`, `recommendationModel`), which is
not PEP 8 — Python convention is `snake_case`. The codebase is internally consistent, so new
code should match the existing style rather than mix the two. A rename to `snake_case` is a
reasonable one-off cleanup, but it must be done in a single pass across all seven modules.

### Adding a new page

1. Create `new_page.py` exporting `renderNewPagePage(<args>, page)`.
2. Create `css/new_page_css.py` exporting `new_page_css()`.
3. Gate the style call: `if page == "New Page": new_page_css()`.
4. Import the renderer in [`main.py`](../main.py) and add an `elif` branch matching the same
   string.
5. Add a button on the preceding page that sets `st.session_state.page = "New Page"` and calls
   `st.rerun()`.

The page identifier string appears in at least three places (router branch, CSS gate, and the
transition that sets it). They must match exactly — there is no enum or constant, so a typo
produces a blank page rather than an error.

### Adding a title to the selection page

1. Add the poster PNG to `mediaImages/`.
2. Add `{"Image": "mediaImages/NewTitle.png", "Title": "Exact Catalogue Title"}` to the
   `movie_selection` list in [`media_selection.py`](../media_selection.py:10).
3. **Verify the title string matches the CSV exactly** — including punctuation and casing.
   A mismatch produces an unhandled `IndexError` when the card is clicked:

```bash
python -c "import pandas as pd; d=pd.read_csv('dataset/movies_and_tv_shows_dataset.csv'); print('Exact Catalogue Title' in set(d['Title']))"
```

The grid is laid out four columns wide, so the list works best at multiples of four.

---

## 4. Testing strategy

**There are currently no tests.** This section describes what to build, ordered by
value-per-effort.

### Tier 1 — data contract tests

Cheapest and highest value. The failure modes they catch are real: every one corresponds to an
unhandled exception in the running app. The full assertion set is in
[DATA.md](DATA.md#6-catalogue-refresh-procedure).

```python
# tests/test_dataset.py
import pandas as pd
import pytest

@pytest.fixture(scope="session")
def dataset():
    return pd.read_csv("dataset/movies_and_tv_shows_dataset.csv")

def test_schema(dataset):
    assert list(dataset.columns) == ["Title", "Genre", "Description"]

def test_no_nulls(dataset):
    assert dataset.isna().sum().sum() == 0

def test_titles_unique(dataset):
    assert dataset["Title"].is_unique

def test_seed_titles_present(dataset):
    from media_selection import SEED_TITLES  # extract the list to a module constant first
    missing = [m["Title"] for m in SEED_TITLES if m["Title"] not in set(dataset["Title"])]
    assert not missing, f"seed titles missing from catalogue: {missing}"

def test_no_html_unsafe_characters(dataset):
    assert not dataset["Title"].str.contains("[<>]", regex=True).any()
    assert not dataset["Description"].str.contains("[<>]", regex=True).any()
```

`test_seed_titles_present` requires extracting the hard-coded `movie_selection` list out of
`renderSelectionPage` into a module-level constant — a worthwhile refactor in its own right,
since it makes the list importable without invoking Streamlit.

### Tier 2 — model unit tests

`recommendationModel` is a pure function with no Streamlit dependency, so it tests directly.

```python
# tests/test_recommendation_model.py
def test_returns_ten_titles(dataset):
    assert len(recommendationModel(dataset, "Breaking Bad")) == 10

def test_excludes_the_query_title(dataset):
    assert "Breaking Bad" not in recommendationModel(dataset, "Breaking Bad")

def test_all_results_exist_in_catalogue(dataset):
    results = recommendationModel(dataset, "Narcos")
    assert set(results) <= set(dataset["Title"])

def test_is_deterministic(dataset):
    assert recommendationModel(dataset, "Squid Game") == recommendationModel(dataset, "Squid Game")

def test_does_not_mutate_caller_dataframe(dataset):
    before = list(dataset.columns)
    recommendationModel(dataset, "Roma")
    assert list(dataset.columns) == before  # currently FAILS — KeyFeatures is added in place
```

The last test **fails against the current implementation** by design — it pins the mutation
bug described in [issue 3](#3-the-model-mutates-its-callers-dataframe) so the fix can be
verified.

Use a small fixture catalogue (50–100 rows) for speed. Against the full dataset each call
allocates ~620 MB and takes seconds, which makes a test suite painful to run.

### Tier 3 — golden-set regression tests

The model is fully deterministic, so its output can be pinned. This catches unintended
behaviour changes from dependency upgrades or feature-engineering tweaks without needing
relevance labels.

```python
# tests/test_golden_recommendations.py
GOLDEN = json.loads(Path("tests/fixtures/golden_recommendations.json").read_text())

@pytest.mark.parametrize("title", GOLDEN)
def test_recommendations_unchanged(dataset, title):
    assert recommendationModel(dataset, title) == GOLDEN[title]
```

Generate the fixture once from a known-good state and review any diff deliberately. Note that
the golden set is coupled to the dataset snapshot — a catalogue refresh invalidates it and it
must be regenerated.

### Tier 4 — scoring tests

```python
def test_relevance_scoring():
    # Yes=1.0, Maybe=0.5, No=0.0, averaged over 10
    responses = [{"Value": 1}] * 5 + [{"Value": 0.5}] * 2 + [{"Value": 0}] * 3
    assert sum(r["Value"] for r in responses) / 10 * 100 == 60.0
```

This requires extracting the scoring arithmetic out of `renderModelAnalysisPage` into a pure
function — see [issue 5](#5-the-recommendation-count-is-duplicated-as-two-constants).

### Tier 5 — UI smoke tests

Streamlit ships [`AppTest`](https://docs.streamlit.io/develop/api-reference/app-testing) for
headless page testing. It can drive the flow end to end without a browser:

```python
from streamlit.testing.v1 import AppTest

def test_selection_page_renders_twenty_cards():
    at = AppTest.from_file("main.py").run()
    assert len(at.button) == 20

def test_clicking_a_title_routes_to_about_media():
    at = AppTest.from_file("main.py").run()
    at.button[0].click().run()
    assert at.session_state.page == "About Media"
```

These are the slowest tests — each run exercises the full pipeline — so keep the count small.

### Recommended tooling

| Tool | Purpose |
| --- | --- |
| `pytest` | Test runner |
| `ruff` | Linting and formatting (fast, single tool) |
| GitHub Actions | Run `ruff check` and `pytest` on push and pull request |

A minimal CI job would be: set up Python 3.12, `pip install -r requirements.txt pytest ruff`,
then `ruff check .` and `pytest`.

---

## 5. Known issues and technical debt

Ordered by impact.

### 1. CSS targets Streamlit's internal class names

**Severity: high — silent breakage**

Selectors such as `.st-emotion-cache-1w723zb`, `.st-emotion-cache-nl76d5`, and
`.st-emotion-cache-1anq8dj` are Emotion CSS-in-JS content hashes generated by Streamlit's
frontend build. They are not a public API and change between releases without notice.

Every layout rule in `css/` — container widths, heading alignment, button colour and width,
grid spacing, image corner radius — depends on these hashes. When they change, **the styling
silently stops applying**. No exception, no warning; the page just renders with default
Streamlit styling.

*Affected:* all five files in `css/`, roughly two-thirds of the rules.

*Fix:* target `data-testid` attributes, which Streamlit documents as stable hooks
(e.g. `[data-testid="stAppViewContainer"]`, `[data-testid="stVerticalBlock"]`), or wrap
content in author-defined containers and style those. The author-defined classes already in
use (`.media-title`, `.accuracy`, `.response-container`) are the correct pattern.

*Interim mitigation:* pin the exact Streamlit version in a lockfile and re-check the styling
visually after every upgrade.

### 2. The model is recomputed on every interaction

**Severity: high — performance**

[`media_recommendations.py:8`](../media_recommendations.py:8) calls `recommendationModel`
unconditionally at the top of the render function. Every Yes/Maybe/No click calls
`st.rerun()`, so a complete 10-recommendation pass rebuilds the TF-IDF matrix and the full
8,807 × 8,807 dense cosine matrix **11 or more times**. That is ~620 MB allocated and
released, repeatedly, to read a single row.

[`main.py:10`](../main.py:10) has the same shape at lower cost: `pd.read_csv` runs on every
rerun.

*Fix:* `@st.cache_resource` on the index build, `@st.cache_data` on the dataset load, and
compute only the query row rather than the full matrix. Detail in
[ARCHITECTURE.md](ARCHITECTURE.md#8-target-architecture) and
[MODEL.md](MODEL.md#5-computational-cost).

### 3. The model mutates its caller's DataFrame

**Severity: medium — correctness hazard**

[`recommendation_model.py:10`](../recommendation_model.py:10) assigns `dataset["KeyFeatures"]`
directly on the passed-in DataFrame. The function reads as pure but is not.

This is harmless today only because Streamlit re-reads the CSV on every rerun, so the added
column never survives. Introduce `@st.cache_data` on the loader — the recommended fix for
issue 2 — and this becomes a live bug: the cached DataFrame accumulates the column, and
re-running the model concatenates onto an already-mutated frame.

*Fix:* build `KeyFeatures` into a local Series rather than assigning into `dataset`.

### 4. Unused cross-page import

**Severity: low — hygiene**

[`model_analysis.py:4`](../model_analysis.py:4) imports `recommendationModel` from
`media_recommendations` and never uses it. It resolves only because `media_recommendations`
re-exports the name, and it creates a page-to-page dependency that violates the module
boundary described in [ARCHITECTURE.md](ARCHITECTURE.md#boundaries-that-hold).

*Fix:* delete the line.

### 5. The recommendation count is duplicated as two constants

**Severity: medium — silent miscalculation**

The count `10` is hard-coded twice, independently:

- [`recommendation_model.py:26`](../recommendation_model.py:26) — the slice `[1:11]`
- [`model_analysis.py:30`](../model_analysis.py:30) — the divisor in `(value / 10) * 100`

Changing either alone corrupts the relevance score without any error. Returning 5
recommendations would cap the reported relevance at 50%.

*Fix:* define a single `RECOMMENDATION_COUNT = 10` and use it in both places.

### 6. No navigation backwards, and Descriptive Analysis is a dead end

**Severity: medium — usability**

The flow is strictly one-way. There is no way to return to the selection page, no way to
re-read the detail page, and no exit from Descriptive Analysis. The only recovery is a browser
refresh, which is not signposted anywhere in the UI.

*Fix:* add a "Start over" control that clears `selected_movie`, `selected_movie_image`,
`recommendation_number`, and `responses`, then reruns. Clearing all four matters — resetting
only `selected_movie` would leave stale responses that corrupt the next session's score.

### 7. No error handling anywhere

**Severity: medium**

No `try`/`except` exists in the codebase. Every failure surfaces as a raw Python traceback in
the browser. The specific unguarded paths:

| Path | Failure |
| --- | --- |
| [`main.py:10`](../main.py:10) | `FileNotFoundError` if the CSV is missing or the process starts in the wrong working directory |
| [`recommendation_model.py:18`](../recommendation_model.py:18) | `IndexError` if the title is not in the catalogue |
| [`about_selected_media.py:17`](../about_selected_media.py:17) | `IndexError` — same cause |
| [`media_selection.py:48`](../media_selection.py:48) | Streamlit media error if a poster PNG is missing |
| [`model_analysis.py:18`](../model_analysis.py:18) | `KeyError` if `responses` is empty |

*Fix:* the data contract tests in [Tier 1](#tier-1-data-contract-tests) prevent most of these
at commit time. A friendly `st.error` on the CSV load path covers the working-directory case,
which is the most common way a new developer hits this.

### 8. Working-directory dependence

**Severity: low — first-run friction**

All paths are relative: `dataset/movies_and_tv_shows_dataset.csv`,
`mediaImages/*.png`. `streamlit run main.py` must be executed from the project root or the
app fails with `FileNotFoundError`.

*Fix:* resolve paths relative to the module —
`Path(__file__).parent / "dataset" / "movies_and_tv_shows_dataset.csv"`.

### 9. Empty stylesheet module

**Severity: trivial**

[`css/descriptive_analysis_css.py`](../css/descriptive_analysis_css.py) injects an empty
`<style>` block. It is harmless and preserves the one-style-module-per-page convention, so it
is reasonable to keep as a placeholder — but it should carry a comment saying so.

### 10. Unreferenced asset

**Severity: trivial**

`mediaImages/movie_temp.png` is referenced by no source file. Delete it or document its
purpose.

### 11. Oversized poster assets

**Severity: low — page weight**

21 unoptimised PNGs totalling ~18 MB for a page showing twenty thumbnails. Negligible on
localhost, significant over a network. Resizing to display dimensions and converting to WebP
would cut this by roughly an order of magnitude.

---

## 6. Security considerations

The application's exposure is genuinely low: it runs locally, reads one static file, writes
nothing, has no authentication, no secrets, no user accounts, no network egress, and no
personal data. The items below are latent rather than active.

### Unescaped HTML interpolation

Three modules interpolate catalogue values directly into HTML with
`unsafe_allow_html=True`:

| Module | Lines |
| --- | --- |
| [`about_selected_media.py`](../about_selected_media.py:26) | 26–28 |
| [`media_recommendations.py`](../media_recommendations.py:33) | 33–35 |
| [`model_analysis.py`](../model_analysis.py:39) | 39–40 |

Measured against the current dataset:

- **0** titles or descriptions contain `<` or `>` — so there is no injection today.
- **179** titles and **8** descriptions contain `&`. Browsers tolerate a bare `&` in most
  positions, so these render acceptably — but by leniency, not correctness.

This is safe only because the catalogue is a trusted, committed, static file. It becomes a
real XSS vector the moment the data source is anything user-writable — an upload, an API, a
database. Escape with `html.escape()` before interpolation regardless; it costs nothing and
removes the class of bug.

### Dependency supply chain

Six third-party packages, installed unpinned from PyPI. `squarify` is a small,
low-maintenance package used for exactly one treemap on one page. Pinning versions in a
lockfile and enabling Dependabot would be proportionate hardening.

### If this is ever deployed publicly

The threat model changes completely. At minimum:

- Bind to a specific interface; do not expose `0.0.0.0:8501` without a reverse proxy.
- Add TLS termination.
- Add authentication if the deployment is not intended to be public.
- Resolve the poster image licensing question in [DATA.md](DATA.md#7-licensing-and-privacy).
- Fix issue 2 first — an uncached 620 MB allocation per click is a trivial denial-of-service
  vector.

See [INFRASTRUCTURE.md](INFRASTRUCTURE.md#5-deployment-options).
