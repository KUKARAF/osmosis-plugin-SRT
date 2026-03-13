import asyncio
import json
import sys

import click

from osmosis_media import fetch_and_process, process_srt


@click.group()
def cli():
    """osmosis-media: extract vocabulary from subtitles for language learning."""


@cli.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Path to SRT file")
@click.option("--lang", "-l", required=True, help="ISO 639-1 language code (e.g. es, ja)")
@click.option("--title", "-t", required=True, help="Media title")
@click.option("--media-type", default="other", show_default=True,
              type=click.Choice(["movie", "series", "book", "other"]))
@click.option("--season", type=int, default=None)
@click.option("--episode", type=int, default=None)
@click.option("--output", "-o", default="json", show_default=True,
              type=click.Choice(["json", "words"]),
              help="json=full MediaGoal, words=one lemma+pos per line")
def process(file, lang, title, media_type, season, episode, output):
    """Process a local SRT file."""
    srt = open(file, encoding="utf-8", errors="replace").read()
    goal = process_srt(
        srt=srt, language=lang, title=title,
        media_type=media_type, season=season, episode=episode,
    )
    _print_output(goal, output)


@cli.command()
@click.option("--title", "-t", required=True, help="Show or movie title")
@click.option("--lang", "-l", required=True, help="ISO 639-1 language code")
@click.option("--season", type=int, default=None)
@click.option("--episode", type=int, default=None)
@click.option("--media-type", default="series", show_default=True,
              type=click.Choice(["movie", "series", "book", "other"]))
@click.option("--provider", default="subdl", show_default=True)
@click.option("--api-key", envvar="SUBDL_API_KEY", help="Provider API key")
@click.option("--output", "-o", default="json", show_default=True,
              type=click.Choice(["json", "words"]))
def fetch(title, lang, season, episode, media_type, provider, api_key, output):
    """Fetch subtitle from a provider and process it."""
    try:
        goal = asyncio.run(fetch_and_process(
            title=title, language=lang, season=season, episode=episode,
            media_type=media_type, provider=provider, api_key=api_key,
        ))
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    _print_output(goal, output)


def _print_output(goal, fmt: str):
    if fmt == "json":
        click.echo(json.dumps(goal.to_dict(), ensure_ascii=False, indent=2))
    elif fmt == "words":
        click.echo(f"# {goal.title} ({goal.language}) — {goal.unique_lemmas} lemmas, {goal.word_count} tokens")
        for w in goal.words:
            forms = ", ".join(w.forms[:4])
            click.echo(f"{w.lemma:<25} {w.pos:<6} freq={w.frequency:<5} forms=[{forms}]")
