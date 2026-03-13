"""
osmosis-media: NLP pipeline for extracting vocabulary from subtitles.

Primary API:
    process_srt()       — process SRT content you already have
    fetch_and_process() — fetch from a subtitle provider then process
"""
from __future__ import annotations

from osmosis_media.models import MediaGoal, Word
from osmosis_media.srt_parser import parse_lines
from osmosis_media.nlp import extract_words

__all__ = ["process_srt", "fetch_and_process", "MediaGoal", "Word"]


def process_srt(
    srt: str,
    language: str,
    title: str,
    *,
    media_type: str = "other",
    season: int | None = None,
    episode: int | None = None,
    source_url: str | None = None,
) -> MediaGoal:
    """
    Process a raw SRT string and return a MediaGoal with lemmatised vocabulary.

    Args:
        srt:        Raw SRT file content.
        language:   ISO 639-1 code (e.g. "es", "ja").
        title:      Human-readable title (e.g. "The Office S01E01").
        media_type: "movie" | "series" | "book" | "other".
        season:     Season number (series only).
        episode:    Episode number (series only).
        source_url: URL the subtitle was fetched from, for provenance.
    """
    lines = parse_lines(srt)
    word_count = sum(len(line.split()) for line in lines)
    words = extract_words(lines, language)

    return MediaGoal(
        title=title,
        media_type=media_type,
        language=language,
        season=season,
        episode=episode,
        words=words,
        raw_srt=srt,
        source_url=source_url,
        word_count=word_count,
        unique_lemmas=len(words),
    )


async def fetch_and_process(
    title: str,
    language: str,
    *,
    season: int | None = None,
    episode: int | None = None,
    provider: str = "subdl",
    api_key: str | None = None,
    media_type: str = "series",
) -> MediaGoal:
    """
    Fetch a subtitle from a provider, then process it into a MediaGoal.

    Subtitle search falls back progressively:
        season + episode → season only → title only

    Args:
        title:      Show or movie title (clean — no "Watch X in Y" framing).
        language:   ISO 639-1 code.
        season:     Season number (series only).
        episode:    Episode number (series only).
        provider:   "subdl" (default) or any registered provider name.
        api_key:    Provider API key (falls back to env var).
        media_type: Passed through to the returned MediaGoal.
    """
    from osmosis_media.providers.subdl import SubDLProvider

    if provider == "subdl":
        p = SubDLProvider(api_key=api_key)
    else:
        raise ValueError(f"Unknown provider: {provider!r}. Available: 'subdl'")

    results = []
    for s, e in [(season, episode), (season, None), (None, None)]:
        results = await p.search(title=title, language=language, season=s, episode=e)
        if results:
            break

    if not results:
        episode_str = f" S{season:02d}E{episode:02d}" if season and episode else ""
        raise ValueError(
            f"No subtitles found for '{title}{episode_str}' in language '{language}'"
        )

    srt = await p.download(results[0])

    full_title = title
    if season is not None and episode is not None:
        full_title = f"{title} S{season:02d}E{episode:02d}"
    elif season is not None:
        full_title = f"{title} S{season:02d}"

    return process_srt(
        srt=srt,
        language=language,
        title=full_title,
        media_type=media_type,
        season=season,
        episode=episode,
        source_url=results[0].url,
    )
