# Data

> Scope: the catalogue in `dataset/movies_and_tv_shows_dataset.csv` and the poster assets in
> `mediaImages/` — where they came from, what they contain, and what to watch out for.
> For how the data is used, see [MODEL.md](MODEL.md).

---

## 1. Provenance

| Field | Value |
| --- | --- |
| Platform | [Kaggle](https://www.kaggle.com/) |
| Dataset | [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows) |
| Author | shivamb |
| Local path | `dataset/movies_and_tv_shows_dataset.csv` |
| Local modification | Reduced from 12 source columns to 3 |
| Snapshot date | Not recorded — the source dataset reflects the Netflix catalogue as of its last Kaggle update, not today's catalogue |
| Update mechanism | Manual. Replace the file and re-verify the 20 seed titles |

**There is no automated refresh.** The CSV is a committed, static snapshot. Nothing in the
application writes to it, and nothing checks whether it is stale.

---

## 2. Schema

```
Title,Genre,Description
```

| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| `Title` | `string` | No (0 nulls) | The name of the movie or TV show. Used as the **de facto primary key** |
| `Genre` | `string` | No (0 nulls) | Comma-separated genre labels, e.g. `International TV Shows, TV Dramas, TV Mysteries` |
| `Description` | `string` | No (0 nulls) | A one- or two-sentence synopsis |

### File properties

| Property | Value |
| --- | --- |
| Format | CSV, RFC 4180 quoting (fields containing commas are double-quoted) |
| Encoding | UTF-8, no BOM |
| Header row | Present |
| Size on disk | 1.7 MB |
| Line count | 8,809 (header + 8,807 records + trailing newline) |
| Read by | `pd.read_csv` with all defaults — [`main.py:10`](../main.py:10) |

### `Title` as a key

`Title` is used as a lookup key in three places
([`recommendation_model.py:18`](../recommendation_model.py:18),
[`about_selected_media.py:17`](../about_selected_media.py:17),
[`media_recommendations.py:32`](../media_recommendations.py:32)), always via exact
string equality.

It works because the current snapshot has **0 duplicate titles** across 8,807 rows. This is a
property of the data, not a guarantee of the file format — there is no uniqueness constraint
anywhere. If a catalogue refresh introduces a duplicate:

- `recommendation_model.py` would take `index.values[0]`, silently picking the first match.
- The `[1:11]` slice, which assumes position 0 is the self-match, would return the duplicate
  as the top recommendation.

A refresh procedure should assert `df["Title"].is_unique`. See
[section 6](#6-catalogue-refresh-procedure).

---

## 3. Profile

Measured on the committed snapshot.

### Volume

| Metric | Value |
| --- | --- |
| Records | 8,807 |
| Columns | 3 |
| Null values | 0 across all columns |
| Duplicate titles | 0 |

### Genre

| Metric | Value |
| --- | --- |
| Distinct genre *combination strings* | 514 |
| Distinct *atomic* genres (after splitting on comma) | 42 |
| Genres per title — mean | 2.19 |
| Genres per title — maximum | 3 |
| Titles with exactly one genre | 2,020 (22.9%) |

**Top 10 atomic genres** — this is the distribution rendered as a treemap on the Descriptive
Analysis page:

| Rank | Genre | Titles |
| --- | --- | --- |
| 1 | International Movies | 2,752 |
| 2 | Dramas | 2,427 |
| 3 | Comedies | 1,674 |
| 4 | International TV Shows | 1,351 |
| 5 | Documentaries | 869 |
| 6 | Action & Adventure | 859 |
| 7 | TV Dramas | 763 |
| 8 | Independent Movies | 756 |
| 9 | Children & Family Movies | 641 |
| 10 | Romantic Movies | 616 |

Genre labels are **not mutually exclusive and not a clean taxonomy**. `International Movies`
is an origin marker rather than a genre, and it is the single most common label. `Dramas` and
`TV Dramas` are separate labels for the same theme split by format. Any analysis that treats
these as a partition will double-count.

### Text

| Metric | Value |
| --- | --- |
| Description length — minimum | 10 words |
| Description length — median | 24 words |
| Description length — mean | 23.9 words |
| Description length — maximum | 48 words |
| Title length — minimum | 1 character |
| Title length — median | 15 characters |
| Title length — maximum | 104 characters |

Descriptions are tightly clustered around 24 words, which is helpful — it means the
description-length bias noted in [MODEL.md](MODEL.md#7-limitations) is mild in practice.

### Character-set notes

| Observation | Count | Why it matters |
| --- | --- | --- |
| Titles containing non-ASCII characters | 223 | Accented and non-Latin titles. Requires UTF-8 throughout; fine with pandas defaults |
| Titles containing `&` | 179 | Interpolated raw into HTML — see below |
| Descriptions containing `&` | 8 | Same |
| Titles or descriptions containing `<` or `>` | **0** | No active HTML-injection risk today |

The absence of `<` and `>` is the only reason the unescaped `st.markdown(...,
unsafe_allow_html=True)` interpolation in the page modules is currently safe. A bare `&` is
tolerated by browsers in most positions, so the 179 `&` titles render acceptably — but they
are relying on error-tolerant HTML parsing, not on correctness. A catalogue refresh that
introduces a `<` would break rendering immediately. See
[ENGINEERING.md](ENGINEERING.md#6-security-considerations).

---

## 4. Columns dropped from the source dataset

The upstream Kaggle dataset carries twelve columns. This project keeps three. The dropped
columns and their relevance:

| Dropped column | Would it improve recommendations? |
| --- | --- |
| `cast` | **Yes, substantially.** Shared actors are one of the strongest cheap similarity signals |
| `director` | **Yes, substantially.** Shared directors strongly predict tonal and stylistic similarity |
| `country` | **Yes, moderately.** Would let the model distinguish origin properly instead of relying on the `International Movies` label |
| `release_year` | Yes, for recency weighting and era matching |
| `rating` | Yes, for age-appropriateness filtering |
| `duration` | Marginal |
| `type` (Movie / TV Show) | **Yes.** Would allow filtering recommendations to the same format as the query |
| `date_added` | No |
| `show_id` | Yes — would give a stable primary key instead of relying on `Title` uniqueness |

Restoring `cast`, `director`, and `type` is the highest-value data change available to this
project and requires no algorithmic work — just adding them to the `KeyFeatures`
concatenation. See [MODEL.md](MODEL.md#improvement-options-cheapest-first).

---

## 5. Poster assets

| Property | Value |
| --- | --- |
| Location | `mediaImages/` |
| Count | 21 PNG files |
| Total size | ~18 MB |
| Largest file | `Shameless.png`, ~1.3 MB |
| Referenced by code | 20 |
| Unreferenced | 1 — `movie_temp.png` appears in no source file |

### Coupling to the dataset

[`media_selection.py:10-31`](../media_selection.py:10) hard-codes a 20-entry list pairing a
poster path with a title string. **Each of those title strings must match a `Title` value in
the CSV exactly**, or the application raises `IndexError` when the user clicks that card.

All 20 have been verified present in the current snapshot:

```
Stranger Things · The Office (U.S.) · Shameless (U.S.) · Squid Game · Cobra Kai
Breaking Bad · Narcos · The Witcher · Peaky Blinders · The Crown · Bird Box
The Irishman · Marriage Story · Enola Holmes · Extraction · The Social Dilemma
Murder Mystery · The Trial of the Chicago 7 · Dolemite Is My Name · ROMA
```

Note the exact spellings that must be preserved: the `(U.S.)` suffixes and the all-caps
`ROMA`.

### Asset sizing

The posters are unoptimised full-resolution PNGs. 18 MB is served for a page that displays
twenty thumbnails. Converting to WebP or resizing to display dimensions would cut this by an
order of magnitude and noticeably improve first-paint time. This matters most if the app is
ever deployed beyond localhost — see
[INFRASTRUCTURE.md](INFRASTRUCTURE.md#3-resource-footprint).

---

## 6. Catalogue refresh procedure

Because the dataset is a manual snapshot, replacing it is a deliberate operation with
verification steps. Run this before committing a new CSV:

```bash
python -c "
import pandas as pd
df = pd.read_csv('dataset/movies_and_tv_shows_dataset.csv')
assert list(df.columns) == ['Title','Genre','Description'], df.columns.tolist()
assert df.isna().sum().sum() == 0, 'null values present'
assert df['Title'].is_unique, 'duplicate titles present'
seeds = ['Stranger Things','The Office (U.S.)','Shameless (U.S.)','Squid Game','Cobra Kai','Breaking Bad','Narcos','The Witcher','Peaky Blinders','The Crown','Bird Box','The Irishman','Marriage Story','Enola Holmes','Extraction','The Social Dilemma','Murder Mystery','The Trial of the Chicago 7','Dolemite Is My Name','ROMA']
missing = [t for t in seeds if t not in set(df['Title'])]
assert not missing, f'seed titles missing from catalogue: {missing}'
assert not df['Title'].str.contains('[<>]', regex=True).any(), 'titles contain HTML-unsafe characters'
assert not df['Description'].str.contains('[<>]', regex=True).any(), 'descriptions contain HTML-unsafe characters'
print(f'OK: {len(df)} rows, all checks passed')
"
```

Each assertion maps to a real failure mode:

| Assertion | Prevents |
| --- | --- |
| Column names | `KeyError` in `recommendation_model.py` |
| No nulls | `TypeError` during string concatenation |
| Unique titles | Wrong row selected; self-match appearing as a recommendation |
| Seed titles present | `IndexError` when a user clicks a poster card |
| No `<` or `>` | Broken or injected HTML on the detail and recommendation pages |

This check belongs in CI once a test suite exists — see
[ENGINEERING.md](ENGINEERING.md#4-testing-strategy).

---

## 7. Licensing and privacy

| Concern | Status |
| --- | --- |
| Dataset licence | Governed by the terms on the [Kaggle dataset page](https://www.kaggle.com/datasets/shivamb/netflix-shows). Verify before any redistribution or commercial use |
| Poster images | Third-party promotional artwork. **No licence has been established for these files.** They are appropriate for private study and portfolio use; clearing rights is required before public deployment |
| Personal data | None. The catalogue contains no personal data. The three retained columns are title, genre, and synopsis |
| User data collected | None persisted. Yes/Maybe/No responses live only in browser-session memory and are destroyed on refresh |
| GDPR / CCPA exposure | None under the current design. Adding response logging would change this — that data would be behavioural data tied to a session |
