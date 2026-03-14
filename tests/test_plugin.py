"""Tests for the osmosis plugin interface."""
import pytest
from osmosis_media.plugin import MediaPlugin


@pytest.fixture
def plugin():
    return MediaPlugin()


def test_name(plugin):
    assert plugin.name == "media"


def test_version(plugin):
    assert plugin.version


def test_get_media_types_contains_expected(plugin):
    types = plugin.get_media_types()
    assert "series" in types
    assert "movie" in types
    assert "book" in types


def test_get_media_types_returns_list(plugin):
    assert isinstance(plugin.get_media_types(), list)


def test_get_goal_actions_returns_list(plugin):
    actions = plugin.get_goal_actions()
    assert isinstance(actions, list)


def test_import_subtitles_action_present(plugin):
    actions = plugin.get_goal_actions()
    ids = [a["id"] for a in actions]
    assert "import_subtitles" in ids


def test_import_subtitles_covers_series_and_movie(plugin):
    actions = plugin.get_goal_actions()
    action = next(a for a in actions if a["id"] == "import_subtitles")
    assert "series" in action["media_types"]
    assert "movie" in action["media_types"]


def test_import_subtitles_not_for_book(plugin):
    actions = plugin.get_goal_actions()
    action = next(a for a in actions if a["id"] == "import_subtitles")
    assert "book" not in action["media_types"]


def test_get_tools_returns_list(plugin):
    assert isinstance(plugin.get_tools(), list)


def test_get_router_returns_none(plugin):
    assert plugin.get_router() is None
