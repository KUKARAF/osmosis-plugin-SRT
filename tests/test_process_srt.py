"""Integration tests for process_srt() — no network, no spaCy model needed."""
import pytest
from osmosis_media import process_srt
from osmosis_media.models import MediaGoal

SRT = """\
1
00:00:01,000 --> 00:00:03,000
El detective encontró las pistas.

2
00:00:04,000 --> 00:00:06,000
Ella corrió hacia la puerta rápidamente.

3
00:00:07,000 --> 00:00:09,000
Los sospechosos huyeron del lugar.
"""


def test_returns_media_goal():
    result = process_srt(SRT, language="es", title="Test Show")
    assert isinstance(result, MediaGoal)


def test_title_and_language_set():
    result = process_srt(SRT, language="es", title="My Show")
    assert result.title == "My Show"
    assert result.language == "es"


def test_media_type_default():
    result = process_srt(SRT, language="es", title="T")
    assert result.media_type == "other"


def test_media_type_override():
    result = process_srt(SRT, language="es", title="T", media_type="series")
    assert result.media_type == "series"


def test_season_episode_stored():
    result = process_srt(SRT, language="es", title="T", season=2, episode=5)
    assert result.season == 2
    assert result.episode == 5


def test_source_url_stored():
    result = process_srt(SRT, language="es", title="T", source_url="http://example.com/sub.srt")
    assert result.source_url == "http://example.com/sub.srt"


def test_word_count_positive():
    result = process_srt(SRT, language="es", title="T")
    assert result.word_count > 0


def test_unique_lemmas_positive():
    result = process_srt(SRT, language="es", title="T")
    assert result.unique_lemmas > 0


def test_words_list_not_empty():
    result = process_srt(SRT, language="es", title="T")
    assert len(result.words) > 0


def test_empty_srt_produces_no_words():
    # pysubs2 can't parse empty string — either raises or returns empty words
    import pysubs2
    try:
        result = process_srt("", language="es", title="T")
        assert result.words == []
        assert result.word_count == 0
    except pysubs2.exceptions.FormatAutodetectionError:
        pass  # acceptable — empty string is not a valid subtitle
