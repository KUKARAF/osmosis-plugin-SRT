"""
NLP pipeline: lemmatisation + POS tagging.

Primary engine: spaCy (full morphological analysis, stop word filtering).
Fallback engine: simplemma (rule-based, no model needed, 30+ languages).
"""
from __future__ import annotations

import re
import warnings
from collections import defaultdict

from osmosis_media.models import Word

# spaCy model names by ISO 639-1 code
SPACY_MODELS: dict[str, str] = {
    "ar": "ar_core_news_md",
    "ca": "ca_core_news_md",
    "da": "da_core_news_md",
    "de": "de_core_news_md",
    "el": "el_core_news_md",
    "en": "en_core_web_md",
    "es": "es_core_news_md",
    "fi": "fi_core_news_md",
    "fr": "fr_core_news_md",
    "hr": "hr_core_news_md",
    "it": "it_core_news_md",
    "ja": "ja_core_news_md",
    "ko": "ko_core_news_md",
    "lt": "lt_core_news_md",
    "nb": "nb_core_news_md",
    "nl": "nl_core_news_md",
    "pl": "pl_core_news_md",
    "pt": "pt_core_news_md",
    "ro": "ro_core_news_md",
    "ru": "ru_core_news_md",
    "sl": "sl_core_news_md",
    "sv": "sv_core_news_md",
    "uk": "uk_core_news_md",
    "zh": "zh_core_web_md",
}

# POS tags to include in vocabulary output
_POS_KEEP = {"NOUN", "VERB", "ADJ", "ADV", "PRON", "ADP", "CCONJ", "SCONJ"}

_POS_MAP = {
    "NOUN": "noun",
    "VERB": "verb",
    "ADJ": "adj",
    "ADV": "adv",
    "PRON": "pron",
    "ADP": "prep",
    "CCONJ": "conj",
    "SCONJ": "conj",
}

_model_cache: dict[str, object] = {}

# Simplemma token pattern: unicode letters including accented chars
_TOKEN_RE = re.compile(r"\b\w{2,}\b", re.UNICODE)


def _load_spacy(language: str):
    if language in _model_cache:
        return _model_cache[language]

    model_name = SPACY_MODELS.get(language)
    if model_name is None:
        return None

    try:
        import spacy
        nlp = spacy.load(model_name, exclude=["ner", "parser"])
        _model_cache[language] = nlp
        return nlp
    except OSError:
        warnings.warn(
            f"spaCy model '{model_name}' not installed. "
            f"Run: python -m spacy download {model_name}\n"
            f"Falling back to simplemma (no POS tagging).",
            stacklevel=3,
        )
        return None


def extract_words(lines: list[str], language: str) -> list[Word]:
    """
    Process dialogue lines and return deduplicated, lemmatised Word list,
    sorted by frequency descending.
    """
    nlp = _load_spacy(language)

    freq: dict[str, int] = defaultdict(int)
    forms: dict[str, set[str]] = defaultdict(set)
    examples: dict[str, str] = {}
    pos_result: dict[str, str] = {}

    if nlp is not None:
        _extract_spacy(nlp, lines, freq, forms, examples, pos_result)
    else:
        _extract_simplemma(language, lines, freq, forms, examples, pos_result)

    words = [
        Word(
            lemma=lemma,
            pos=pos_result.get(lemma, "other"),
            frequency=count,
            forms=sorted(forms[lemma]),
            example=examples.get(lemma),
        )
        for lemma, count in freq.items()
    ]
    words.sort(key=lambda w: w.frequency, reverse=True)
    return words


def _extract_spacy(nlp, lines, freq, forms, examples, pos_result):
    for line in nlp.pipe(lines, batch_size=64):
        for token in line:
            if (
                token.is_stop
                or token.is_punct
                or token.is_space
                or token.like_num
                or token.pos_ == "PROPN"
                or token.pos_ not in _POS_KEEP
            ):
                continue
            lemma = token.lemma_.lower().strip()
            if len(lemma) < 2:
                continue
            freq[lemma] += 1
            forms[lemma].add(token.text.lower())
            if lemma not in examples:
                examples[lemma] = line.text
            pos_result[lemma] = _POS_MAP.get(token.pos_, "other")


def _extract_simplemma(language, lines, freq, forms, examples, pos_result):
    try:
        import simplemma
        langdata = simplemma.load_data(language)
    except (ImportError, ValueError):
        # Last resort: no lemmatisation at all, just lowercase tokens
        langdata = None

    for line in lines:
        for token in _TOKEN_RE.findall(line.lower()):
            if len(token) < 2:
                continue
            if langdata is not None:
                import simplemma
                lemma = simplemma.lemmatize(token, langdata)
            else:
                lemma = token
            freq[lemma] += 1
            forms[lemma].add(token)
            if lemma not in examples:
                examples[lemma] = line
            if lemma not in pos_result:
                pos_result[lemma] = "other"
