# Contributing

Thanks for working on this project. This guide covers how to get set up, what to check before
opening a change, and the conventions the codebase follows.

Read [docs/ENGINEERING.md](docs/ENGINEERING.md) first — it has the code map, the full
conventions list, and the outstanding technical debt.

---

## Getting set up

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

Windows PowerShell: `.venv\Scripts\Activate.ps1`

```bash
pip install -r requirements.txt
```

```bash
streamlit run main.py
```

You need **Python 3.12+** and **Streamlit 1.52.0 or newer**. The Streamlit floor is a hard
requirement — the app fails on first render below it. See
[docs/ENGINEERING.md](docs/ENGINEERING.md#the-streamlit-152-floor).

Run from the project root. All file paths in the code are relative to the working directory.

---

## Before you open a change

There is no CI and no test suite yet, so verification is manual. Work through this list.

### Always

- [ ] The app starts: `streamlit run main.py` with no traceback
- [ ] The full flow works end to end — pick a title, read the detail page, rate all 10
      recommendations, view the analysis, view the descriptive charts
- [ ] No new Streamlit deprecation warnings in the terminal

### If you touched the dataset

- [ ] The contract checks in [docs/DATA.md](docs/DATA.md#6-catalogue-refresh-procedure) pass.
      They verify schema, nulls, title uniqueness, seed-title presence, and HTML-unsafe
      characters — each corresponds to an unhandled crash in the running app.

### If you touched `css/`

- [ ] All five pages render correctly, not just the one you changed
- [ ] Note the Streamlit version you verified against in the pull request description

Styling is coupled to Streamlit's internal class names, so "it looks right on my machine" is
version-specific information worth recording.

### If you touched the model

- [ ] Recommendations for at least three different seed titles still look sensible
- [ ] You checked the performance impact — the pipeline already runs 11+ times per session,
      so anything that makes a single call slower is multiplied

### If you upgraded Streamlit

- [ ] All five pages visually verified — an upgrade can silently break the layout
      ([why](docs/ENGINEERING.md#1-css-targets-streamlits-internal-class-names))
- [ ] `requirements.txt` floor updated if you relied on a newer API

---

## Conventions

Match the existing style. The codebase is internally consistent; mixing styles is worse than
either style alone.

| | Convention |
| --- | --- |
| Page entry points | `render<PageName>Page(...)`, `lowerCamelCase` |
| Module names | `snake_case`, named after the page |
| Style modules | One per page in `css/`, no arguments |
| CSS gating | `if page == "<Page Name>": <page>_css()` |
| Transitions | Set `st.session_state.page`, **then** `st.rerun()` — anything after the rerun is unreachable |
| Comments | Inline `#` comments explaining intent, matching the existing density |

Function names are `lowerCamelCase`, which is not PEP 8. This is deliberate consistency with
the existing code, not an oversight. If you want to move the project to `snake_case`, do it as
a single dedicated change across all seven modules — not piecemeal.

### CSS: avoid `.st-emotion-cache-*` selectors

Those class names are Streamlit-generated content hashes that change between releases. Prefer:

1. Author-defined classes on `<div>`s this codebase emits — the pattern already used by
   `.media-title`, `.accuracy`, `.response-container`.
2. `data-testid` attribute selectors for Streamlit internals, e.g.
   `[data-testid="stAppViewContainer"]`.

Adding new Emotion-hash selectors deepens an existing problem. See
[docs/ENGINEERING.md](docs/ENGINEERING.md#1-css-targets-streamlits-internal-class-names).

### Escape interpolated data

If you add an `st.markdown(..., unsafe_allow_html=True)` call that includes dataset values,
run them through `html.escape()` first. The current code does not, and it is safe only because
the committed catalogue happens to contain no `<` or `>`.

---

## Adding a title to the selection page

1. Add the poster PNG to `mediaImages/`.
2. Add `{"Image": "mediaImages/NewTitle.png", "Title": "Exact Catalogue Title"}` to the
   `movie_selection` list in [`media_selection.py`](media_selection.py:10).
3. Verify the title matches the CSV **exactly**, including punctuation and casing:

```bash
python -c "import pandas as pd; d=pd.read_csv('dataset/movies_and_tv_shows_dataset.csv'); print('Exact Catalogue Title' in set(d['Title']))"
```

A mismatch produces an unhandled `IndexError` when someone clicks the card. The grid is four
columns wide, so the list works best at multiples of four.

---

## Adding a page

1. Create `new_page.py` exporting `renderNewPagePage(<args>, page)`.
2. Create `css/new_page_css.py` exporting `new_page_css()`.
3. Gate the style call on the page name.
4. Import the renderer in [`main.py`](main.py) and add an `elif` branch with the same string.
5. Add a button on the preceding page that sets `st.session_state.page` and calls
   `st.rerun()`.

The page identifier string appears in at least three places with no shared constant. A typo
gives you a blank page, not an error — check the spelling in all three.

---

## Good first contributions

These are well-scoped, clearly valuable, and independent of each other. All are described in
detail in [docs/ENGINEERING.md](docs/ENGINEERING.md#5-known-issues-and-technical-debt).

| Change | Why |
| --- | --- |
| Delete the unused `recommendationModel` import in `model_analysis.py:4` | One line; removes a module-boundary violation |
| Delete the unreferenced `mediaImages/movie_temp.png` | One file; no code references it |
| Extract `RECOMMENDATION_COUNT = 10` as a shared constant | Removes a silent score-corruption trap |
| Stop mutating the caller's DataFrame in `recommendation_model.py:10` | Becomes a live bug the moment caching is added |
| Add `@st.cache_data` to the dataset load | Removes a disk read per interaction |
| Add `@st.cache_resource` to the index build and compute a single similarity row | **Highest impact in the project** — turns a 620 MB, multi-second operation into a sub-millisecond one |
| Add a "Start over" button | Fixes the dead-end navigation. Remember to clear all four state keys |
| Add the Tier 1 data contract tests | Prevents the most common crash class |
| Resolve paths relative to `__file__` | Removes the working-directory dependence |

---

## Documentation

Documentation is part of the change, not a follow-up.

- Behaviour change → update the relevant `docs/` file in the same commit
- New dependency → update `requirements.txt` **and** the dependency table in
  [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md#2-dependencies)
- Fixed a listed issue → remove it from
  [docs/ENGINEERING.md](docs/ENGINEERING.md#5-known-issues-and-technical-debt)
- User-visible change → add a [CHANGELOG.md](CHANGELOG.md) entry under `Unreleased`

---

## Commit messages

Short imperative subject line, and explain *why* in the body when the reason is not obvious
from the diff.

```
Cache the TF-IDF index with st.cache_resource

The model was rebuilt on every rerun, so a single 10-recommendation pass
allocated the 620 MB cosine matrix 11 times. Caching the index makes it
once per process.
```
