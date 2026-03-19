# osmosis-media

NLP pipeline for extracting vocabulary from subtitles for language learning. Usable as a standalone CLI tool, a library, or an [osmosis](https://github.com/KUKARAF/osmosis) plugin.

## Install

```bash
uv pip install osmosis-media
# install a spaCy language model for the target language, e.g.:
uv run python -m spacy download es_core_news_md
```

## Running tests

```bash
uv run --extra dev pytest tests/ -v
```

## How to contribute

1. Install [pre-commit](https://pre-commit.com/):

   ```bash
   uv tool install pre-commit
   pre-commit install
   ```

   This runs the test suite automatically before every commit.

2. Create a feature branch:

   ```bash
   git checkout -b my-feature
   ```

3. Make your changes, then run the tests manually if you like:

   ```bash
   uv run --extra dev pytest tests/ -v
   ```

4. Commit and push. The pre-commit hook will run `pytest` — if tests fail the commit is blocked.

5. Open a pull request against `main`.
