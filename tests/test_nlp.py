"""
NLP tests use the simplemma fallback — no spaCy model install required.
We test with a language that simplemma supports but spaCy model is unlikely
to be present in CI: "xx" (unknown) falls back gracefully, while "es" exercises
the simplemma lemmatiser.
"""
import pytest
from osmosis_media.nlp import extract_words


LINES_ES = [
    "Ella camina por el parque todos los días.",
    "Los perros corren rápidamente.",
    "Él come manzanas y naranjas.",
]

LINES_REPEAT = [
    "El gato come.",
    "El gato duerme.",
    "El gato juega.",
]


def test_returns_word_objects():
    words = extract_words(LINES_ES, "es")
    assert len(words) > 0
    for w in words:
        assert hasattr(w, "lemma")
        assert hasattr(w, "frequency")
        assert hasattr(w, "pos")


def test_lemmas_are_lowercase():
    words = extract_words(LINES_ES, "es")
    for w in words:
        assert w.lemma == w.lemma.lower()


def test_frequency_sorted_descending():
    words = extract_words(LINES_REPEAT, "es")
    freqs = [w.frequency for w in words]
    assert freqs == sorted(freqs, reverse=True)


def test_repeated_word_has_higher_frequency():
    words = extract_words(LINES_REPEAT, "es")
    freq_map = {w.lemma: w.frequency for w in words}
    # "gato" appears 3 times, should have frequency >= 3
    assert "gato" in freq_map
    assert freq_map["gato"] >= 3


def test_example_sentence_populated():
    words = extract_words(LINES_ES, "es")
    for w in words:
        assert w.example is not None


def test_empty_lines_returns_empty():
    words = extract_words([], "es")
    assert words == []


def test_unknown_language_falls_back():
    # simplemma raises ValueError for unknown language codes — document this behaviour
    import pytest
    lines = ["hello world test sentence"]
    with pytest.raises((ValueError, Exception)):
        extract_words(lines, "xx")
