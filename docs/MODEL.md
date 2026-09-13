# The Recommendation Model

> Scope: the algorithm in [`recommendation_model.py`](../recommendation_model.py) and the
> relevance scoring in [`model_analysis.py`](../model_analysis.py) — what they compute, how,
> at what cost, and where they fall down.
> For the data they run on see [DATA.md](DATA.md).

---

## 1. Summary

| Property | Value |
| --- | --- |
| Family | Content-based filtering |
| Representation | TF-IDF over bag-of-words |
| Similarity measure | Cosine similarity |
| Training | None — the model is built from the corpus at call time |
| Persisted artefact | None |
| Output | Top 10 most similar titles, excluding the query title |
| Determinism | Fully deterministic. Same dataset + same title = same 10 results, always |
| Library | scikit-learn (`TfidfVectorizer`, `cosine_similarity`) |

There is no supervised learning here: nothing is fit to labels, there is no train/test split,
and no parameters are learned beyond the corpus-level IDF statistics. The model is a
similarity search over a fixed text index.

---

## 2. Feature engineering

Three columns are concatenated, space-separated, into a single synthetic text field:

```python
dataset["KeyFeatures"] = dataset["Title"] + ' ' + dataset["Description"] + ' ' + dataset["Genre"]
```

Example for one row:

| Column | Value |
| --- | --- |
| `Title` | `Blood & Water` |
| `Genre` | `International TV Shows, TV Dramas, TV Mysteries` |
| `Description` | `After crossing paths at a party, a Cape Town teen sets out to prove whether a private-school swimming star is her sister who was abducted at birth.` |
| **`KeyFeatures`** | `Blood & Water After crossing paths at a party, ... International TV Shows, TV Dramas, TV Mysteries` |

### Consequences of this design

- **All three fields share one vocabulary space.** The word "drama" in a description and
  "Dramas" in a genre are *different tokens* (`drama` vs `dramas`) because there is no
  stemming or lemmatisation.
- **No field weighting.** A genre term and a description term contribute identically. Because
  descriptions run ~25 words and genres ~2-4, descriptions dominate the signal by volume.
- **Genre strings are tokenised, not treated as categories.** `International TV Shows` becomes
  three tokens — `international`, `tv`, `shows` — and `tv` and `shows` are extremely common,
  so IDF drives their weight close to zero. The genre signal is weaker than it looks.
- **Titles leak into the feature space.** Sequels and franchise entries that share words with
  the query title score highly for lexical rather than thematic reasons. This is often a
  desirable behaviour here (a user picking *Narcos* plausibly wants *Narcos: Mexico*) but it
  is an accident of the design, not an intent.

---

## 3. Vectorisation

```python
vectorizer = TfidfVectorizer(stop_words='english')
vectorized_features = vectorizer.fit_transform(dataset["KeyFeatures"])
```

All `TfidfVectorizer` defaults apply except `stop_words`:

| Parameter | Value | Effect |
| --- | --- | --- |
| `stop_words` | `'english'` | Drops scikit-learn's 318-word English stop list (`and`, `is`, `or`, ...) |
| `lowercase` | `True` (default) | Case is discarded |
| `token_pattern` | `(?u)\b\w\w+\b` (default) | Tokens are runs of 2+ word characters. **Single-character tokens and all punctuation are dropped** |
| `ngram_range` | `(1, 1)` (default) | Unigrams only. No phrases — `"cape town"` is two independent tokens |
| `norm` | `'l2'` (default) | Each row is unit-normalised, which is what makes cosine similarity equal a dot product |
| `sublinear_tf` | `False` (default) | Raw term frequency, not `1 + log(tf)` |
| `min_df` / `max_df` | `1` / `1.0` (defaults) | No vocabulary pruning. Terms appearing in exactly one document are kept |

### Resulting matrix shape

Measured against the current dataset:

| Quantity | Value |
| --- | --- |
| Documents | 8,807 |
| Vocabulary | ~22,600 terms before stop-word removal; ~22,300 after |
| Non-zero entries | ~240,000 |
| Mean terms per document | ~27 |
| Density | ~0.12% — the matrix is extremely sparse |

Because `min_df=1`, roughly half the vocabulary consists of terms that appear in a single
title (proper nouns, place names, character names). Those terms carry maximum IDF weight, so
**a single rare shared word can dominate a similarity score**. Two unrelated films that both
mention an unusual city name will be pulled together more strongly than two films that share
a genre.

---

## 4. Similarity and ranking

```python
similarity_matrix = cosine_similarity(vectorized_features)

selected_media_index = dataset[dataset["Title"] == selectedTitle].index.values[0]

similarity_score = list(enumerate(similarity_matrix[selected_media_index]))
sorted_media_by_similarity_score = sorted(similarity_score, key=lambda x: x[1], reverse=True)

for i in sorted_media_by_similarity_score[1:11]:
    ...
```

### Cosine similarity

For unit-normalised TF-IDF vectors **a** and **b**:

```
cos(a, b) = (a · b) / (||a|| ||b||) = a · b        (since ||a|| = ||b|| = 1)
```

The score lies in `[0, 1]` — TF-IDF values are non-negative, so it can never go negative.
`0` means no shared vocabulary at all; `1` means identical term distributions.

### The `[1:11]` slice

Index `0` of the sorted list is dropped because the query title is always its own best match,
with a self-similarity of exactly `1.0`. This is correct **only if no other row ties at 1.0**
and no duplicate titles exist. Both conditions hold for the current dataset: there are
**0 duplicate titles** across 8,807 rows. If a future catalogue update introduces a duplicate
title, `[1:11]` would return the duplicate as the first "recommendation" and
`index.values[0]` would silently pick whichever row came first.

### Tie-breaking

Python's `sorted` is stable, so ties in similarity score are broken by original DataFrame
order — effectively by the catalogue's own row order. This is arbitrary but deterministic.

---

## 5. Computational cost

This is the model's defining practical problem.

### Per call

| Step | Cost |
| --- | --- |
| String concatenation over 8,807 rows | Negligible |
| `TfidfVectorizer.fit_transform` | O(total tokens) ≈ 240k operations. Sub-second |
| `cosine_similarity(X)` | **O(n² · density)** sparse matrix product, then materialised **dense** |
| Dense result allocation | 8,807 × 8,807 × 8 bytes = **620,505,992 bytes ≈ 620 MB (592 MiB)** |
| Sort of one row | O(n log n) on 8,807 elements. Negligible |

**The dense similarity matrix is ~620 MB** and only one of its 8,807 rows is ever read.
The other 99.99% is computed, allocated, and discarded.

### Per session

`recommendationModel` is invoked unconditionally at the top of `renderRecommendationsPage`,
and every Yes/Maybe/No click triggers `st.rerun()`. A full 10-recommendation pass therefore
performs the whole pipeline **11+ times**: once on arrival, then once per rating.

| | Current | With caching |
| --- | --- | --- |
| Matrix builds per session | 11+ | 1 |
| Peak allocation | ~620 MB, repeatedly | ~620 MB once, or ~70 KB with a single-row computation |
| CSV reads per session | 1 per rerun (~15+) | 1 |

### Scaling

Memory grows with the **square** of catalogue size:

| Catalogue size | Dense matrix size |
| --- | --- |
| 8,807 (today) | 620 MB |
| 20,000 | 3.2 GB |
| 50,000 | 20 GB |
| 100,000 | 80 GB |

The dense-matrix approach is therefore a hard ceiling at roughly the current catalogue size on
an 8 GB machine. The fix is not more RAM — it is to never build the full matrix:

```python
# Only the query row is ever used. This needs ~70 KB, not 620 MB.
row = cosine_similarity(vectorized_features[selected_media_index], vectorized_features).ravel()
```

Combined with `@st.cache_resource` on the vectoriser, this makes recommendation effectively
instantaneous and removes the memory ceiling entirely. See
[ARCHITECTURE.md](ARCHITECTURE.md#8-target-architecture).

---

## 6. Relevance scoring

[`model_analysis.py`](../model_analysis.py) turns the user's ratings into a percentage.

### Scoring scale

| Response | Value |
| --- | --- |
| Yes | `1.0` |
| Maybe | `0.5` |
| No | `0.0` |

### Formula

```python
accuracy = (value_of_responses / 10) * 100
```

That is, the mean rating across the 10 recommendations, expressed as a percentage. The range
is `0%` (every recommendation rejected) to `100%` (every recommendation accepted), in steps of
5 percentage points.

### What this metric is and is not

**It is** a single user's in-session satisfaction with 10 suggestions. That is a legitimate
and honest signal — it is the user's own judgement, not a proxy.

**It is not** model accuracy in the machine-learning sense. There are no ground-truth labels,
no held-out set, and no baseline to compare against. The UI wording ("The Recommendation Model
was X% relevant!") is accurate; the internal variable name `accuracy` is a misnomer and should
be renamed `relevance_score`.

### Known coupling

The divisor `10` is hard-coded in `model_analysis.py`, while the recommendation count is
hard-coded independently as the slice `[1:11]` in `recommendation_model.py`. **Changing one
without the other silently corrupts the score** — returning 5 recommendations would cap the
displayed relevance at 50%. These two constants should be a single shared value.

### Statistical caveats

- **n = 10.** The standard error on a proportion at n=10 is roughly 16 percentage points. A
  "70% relevant" result is not meaningfully different from a "50% relevant" one.
- **No persistence.** Responses live in `st.session_state` and are lost on refresh. There is
  no way to aggregate across users or sessions, so the score cannot be tracked over time or
  used to compare model changes.
- **Order effects are uncontrolled.** Recommendations are always shown best-first, so early
  items are systematically stronger than later ones. A user who fatigues and starts clicking
  "No" depresses the score for reasons unrelated to model quality.

---

## 7. Limitations

### Algorithmic

| Limitation | Effect |
| --- | --- |
| **No semantic understanding** | "Murder" and "homicide" are unrelated tokens. Two thrillers described with different vocabulary score near zero |
| **No stemming or lemmatisation** | `drama` / `dramas` / `dramatic` are three separate features, splitting the signal |
| **Unigrams only** | `"World War II"` contributes three common tokens rather than one meaningful phrase |
| **Rare-term dominance** | With `min_df=1`, one shared proper noun can outrank a genuine thematic match |
| **Description length bias** | Titles with longer descriptions have more tokens and more chances to match, independent of relevance |
| **No popularity or recency signal** | An obscure 1970s film ranks identically to a flagship series if the text matches |
| **Cold-start on metadata quality** | A title with a vague one-line description gets poor recommendations no matter what |
| **Filter bubble by construction** | Content-based similarity cannot surface anything outside the query's lexical neighbourhood. There is no serendipity |

### Data-driven

The catalogue carries only `Title`, `Genre`, and `Description`. The upstream Kaggle dataset
has cast, director, country, release year, rating, and duration — all dropped. Cast and
director in particular are strong, cheap similarity signals for exactly this task. See
[DATA.md](DATA.md#4-columns-dropped-from-the-source-dataset).

### Implementation

| Issue | Location | Impact |
| --- | --- | --- |
| Full pipeline recomputed per interaction | `media_recommendations.py:8` | ~11x wasted work per session |
| Dense 620 MB matrix materialised | `recommendation_model.py:15` | Memory ceiling, slow allocation |
| Caller's DataFrame mutated in place | `recommendation_model.py:10` | Side effect on a "pure" function |
| `IndexError` if title is absent | `recommendation_model.py:18` | Unhandled crash. Safe today — all 20 seed titles verified present — but brittle |
| Recommendation count duplicated as two constants | `recommendation_model.py:26`, `model_analysis.py:30` | Silent score corruption if either changes |

---

## 8. Evaluation and possible improvements

### How to evaluate changes

There is no offline evaluation harness. Because the model is deterministic, the cheapest
meaningful test is a **golden-set regression test**: pin the expected top-10 for each of the
20 seed titles, then assert that a change either reproduces them or produces a reviewed diff.
This catches accidental behaviour changes without needing labels. See
[ENGINEERING.md](ENGINEERING.md#4-testing-strategy).

### Improvement options, cheapest first

| Change | Effort | Expected effect |
| --- | --- | --- |
| Cache the vectoriser and compute a single similarity row | Low | Removes the performance and memory problem entirely. No change to results |
| Restore `Cast`, `Director`, `Country` from the source dataset into `KeyFeatures` | Low | Materially better matches — shared cast and director are strong relevance signals |
| Set `min_df=2` | Low | Drops ~half the vocabulary (single-occurrence terms), reducing rare-term noise |
| Add `ngram_range=(1, 2)` | Low | Captures phrases. Increases vocabulary and memory |
| Weight genre terms (repeat or boost them) | Low | Rebalances the description-dominated signal |
| Treat genres as multi-hot categorical features alongside TF-IDF text | Medium | Clean separation of categorical and free-text signal |
| Swap TF-IDF for sentence embeddings (e.g. a sentence-transformer) | Medium | Real semantic matching — synonyms and paraphrases work. Adds a heavy dependency |
| Approximate nearest neighbours (FAISS, Annoy, `sklearn.neighbors`) | Medium | Sub-linear lookup; removes the n² ceiling for large catalogues |
| Log responses to disk and build a hybrid content + collaborative model | High | Learns actual taste. Requires a persistence layer and enough users to matter |
