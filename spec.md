# osmosis-media — specification

A standalone Python library that ingests media (subtitle files, books) and produces
structured vocabulary-learning objects compatible with the osmosis language learning
service. Installable as a pip package. No dependency on osmosis itself.

---

## Goals

1. Accept an SRT file (or fetch one automatically via a subtitle provider)
2. Perform NLP processing: lemmatize, POS-tag, deduplicate, rank by frequency
3. Return a `MediaGoal` object that the osmosis service can import
4. Be usable independently — as a CLI tool, a library, or an osmosis plugin

---

## Package

```
osmosis-media
```

Install:

```bash
pip install osmosis-media
# install a spaCy language model for the target language, e.g.:
python -m spacy download es_core_news_md
```

---

## Core data model

### `Word`

Represents a single vocabulary item extracted from the media.

| Field         | Type            | Description                                       |
|---------------|-----------------|---------------------------------------------------|
| `lemma`       | `str`           | Dictionary/base form (e.g. `correr`, `run`)       |
| `pos`         | `str`           | Part of speech: `noun`, `verb`, `adj`, `adv`, `pron`, `prep`, `conj`, `other` |
| `frequency`   | `int`           | Number of times this lemma appears in the source  |
| `forms`       | `list[str]`     | Surface forms found (e.g. `["corrió", "corren"]`) |
| `example`     | `str \| None`   | One example subtitle line containing this word    |
| `cefr_hint`   | `str \| None`   | Estimated CEFR level if derivable (`A1`–`C2`)     |

### `MediaGoal`

The primary output object. Duck-typed — osmosis checks for these attributes
without importing this package.

| Field           | Type              | Description                                             |
|-----------------|-------------------|---------------------------------------------------------|
| `title`         | `str`             | Human-readable title (e.g. `"The Office S01E01"`)       |
| `media_type`    | `str`             | `"movie"`, `"series"`, `"book"`, `"other"`              |
| `language`      | `str`             | ISO 639-1 code (e.g. `"es"`, `"ja"`, `"fr"`)           |
| `season`        | `int \| None`     | Season number for series                                |
| `episode`       | `int \| None`     | Episode number for series                               |
| `words`         | `list[Word]`      | Deduplicated, lemmatized vocabulary, sorted by frequency desc |
| `raw_srt`       | `str \| None`     | Original SRT content (for storage / re-processing)      |
| `source_url`    | `str \| None`     | URL the subtitle was fetched from                       |
| `word_count`    | `int`             | Total token count before deduplication                  |
| `unique_lemmas` | `int`             | Count of unique lemmas                                  |

---

## NLP pipeline

### 1. SRT parsing

Strip subtitle formatting to get clean dialogue lines:

- Remove sequence numbers (lines that are just digits)
- Remove timestamp lines (`00:00:01,000 --> 00:00:03,500`)
- Strip HTML/ASS tags (`<i>`, `{\an8}`, etc.)
- Collect non-empty text lines, preserving one example sentence per word

### 2. Tokenisation & lemmatisation

Use **spaCy** with the appropriate language model:

```
es → es_core_news_md   (Spanish)
en → en_core_web_md    (English)
ja → ja_core_news_md   (Japanese)
fr → fr_core_news_md   (French)
de → de_core_news_md   (German)
pt → pt_core_news_md   (Portuguese)
```

For languages without a spaCy model, fall back to **simplemma** (lightweight
rule-based lemmatiser, no ML, supports 30+ languages) with a warning.

### 3. Filtering

Discard tokens that are:
- Punctuation, whitespace, or numeric
- Stop words (spaCy's built-in list for the language)
- Shorter than 2 characters after lemmatisation
- Proper nouns (`PROPN`) — character names clutter the deck

Keep:
- `NOUN`, `VERB`, `ADJ`, `ADV` → maps to `pos` values `noun/verb/adj/adv`
- `PRON`, `ADP`, `CCONJ`, `SCONJ` → maps to `pron/prep/conj`
- Everything else → `other`

### 4. Deduplication & ranking

Group by lemma, accumulate:
- `frequency`: count of occurrences across all subtitle lines
- `forms`: unique surface forms seen
- `example`: first subtitle line where the lemma appeared

Sort by `frequency` descending so the most useful words come first.

---

## Subtitle providers

Providers are pluggable. The built-in provider is SubDL.

### Interface

```python
class SubtitleProvider(Protocol):
    async def search(
        self,
        title: str,
        language: str,
        season: int | None,
        episode: int | None,
    ) -> list[SubtitleResult]: ...

    async def download(self, result: SubtitleResult) -> str:
        """Return raw SRT content."""
        ...
```

### `SubtitleResult`

| Field   | Type  | Description                   |
|---------|-------|-------------------------------|
| `name`  | `str` | Subtitle file/release name    |
| `url`   | `str` | Provider-specific download URL |
| `lang`  | `str` | Language code as returned by provider |

### Built-in providers

| Provider | Class            | Requires            |
|----------|------------------|---------------------|
| SubDL    | `SubDLProvider`  | `SUBDL_API_KEY` env |

SubDL search strategy: try `season+episode`, fall back to `season only`,
fall back to title only. Take the top result.

---

## Public API

### `process_srt(srt, language, title, *, media_type, season, episode, source_url) -> MediaGoal`

Process a raw SRT string you already have.

```python
from osmosis_media import process_srt

goal = process_srt(
    srt=open("the_office_s01e01.es.srt").read(),
    language="es",
    title="The Office S01E01",
    media_type="series",
    season=1,
    episode=1,
)
```

### `fetch_and_process(title, language, *, season, episode, provider, api_key) -> MediaGoal`

Fetch the subtitle automatically then process it.

```python
from osmosis_media import fetch_and_process

goal = await fetch_and_process(
    title="The Office",
    language="es",
    season=1,
    episode=1,
)
```

### `load_model(language) -> None`

Pre-load the spaCy model for a language (optional — auto-loaded on first use).

---

## osmosis integration

osmosis imports a `MediaGoal` via duck typing — no `isinstance` check, just
attribute access. The importer verifies:

```python
def _is_media_goal(obj) -> bool:
    return all(hasattr(obj, attr) for attr in (
        "title", "language", "media_type", "words"
    ))
```

Each `Word` in `goal.words` maps to one `SRSCard`:

| `Word` field | `SRSCard` field  |
|--------------|------------------|
| `lemma`      | `front`          |
| `pos`        | part of `back` (e.g. `"[verb]"`) |
| `example`    | `context_sentence` |
| `frequency`  | stored in card metadata (future) |

Cards are linked to the `Goal` via `GoalWord`. Progress is shared across goals —
if the user already has a card for a lemma, it is linked without resetting FSRS state.

---

## CLI

```bash
# Process a local file
osmosis-media process --file office_s01e01.srt --lang es --title "The Office S01E01"

# Fetch and process automatically
osmosis-media fetch --title "The Office" --lang es --season 1 --episode 1

# Output formats
--output json      # default: prints MediaGoal as JSON
--output words     # one lemma per line with frequency
--output osmosis   # POST directly to a running osmosis instance
```

---

## Project layout

```
osmosis-media/
├── spec.md
├── pyproject.toml
├── README.md
└── osmosis_media/
    ├── __init__.py          # public API: process_srt, fetch_and_process
    ├── models.py            # Word, MediaGoal dataclasses
    ├── srt_parser.py        # strip SRT formatting → clean lines
    ├── nlp.py               # spaCy/simplemma pipeline
    ├── providers/
    │   ├── __init__.py
    │   ├── base.py          # SubtitleProvider Protocol, SubtitleResult
    │   └── subdl.py         # SubDLProvider
    └── cli.py               # click CLI entry point
```

---

## Dependencies

| Package      | Purpose                         | Optional |
|--------------|---------------------------------|----------|
| `spacy`      | Lemmatisation + POS tagging     | No       |
| `simplemma`  | Fallback lemmatiser             | No       |
| `httpx`      | Async HTTP for subtitle fetching | No      |
| `click`      | CLI                             | No       |
| `spacy[lang_models]` | Language-specific models | Yes — install per language |

---

## Open questions

- **Books**: Likely accept plain text or EPUB. Out of scope for v1, noted for v2.
- **CEFR hints**: Could use a frequency-list lookup (e.g. SUBTLEX) to assign
  approximate CEFR levels. Not in v1.
- **Proper nouns**: Filtered by default, but important characters' names might
  be worth keeping. Could add a `--keep-proper-nouns` flag.
- **Phrase extraction**: spaCy noun chunks and verb phrases could surface
  multi-word expressions worth learning as units. v2 feature.
