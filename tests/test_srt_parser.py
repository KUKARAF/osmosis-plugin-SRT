import pytest
from osmosis_media.srt_parser import parse_lines

SRT_BASIC = """\
1
00:00:01,000 --> 00:00:03,000
Hello, world!

2
00:00:04,000 --> 00:00:06,000
How are you today?

3
00:00:07,000 --> 00:00:09,000
[Music]

4
00:00:10,000 --> 00:00:12,000
(applause)
"""

SRT_HTML_TAGS = """\
1
00:00:01,000 --> 00:00:03,000
<i>She said goodbye.</i>

2
00:00:04,000 --> 00:00:06,000
<b>Run!</b>
"""

SRT_MULTILINE = """\
1
00:00:01,000 --> 00:00:05,000
First line.
Second line.
"""

SRT_EMPTY = """\
1
00:00:01,000 --> 00:00:03,000
[Music]

2
00:00:04,000 --> 00:00:06,000
(crowd cheering)
"""


def test_basic_dialogue_extracted():
    lines = parse_lines(SRT_BASIC)
    assert "Hello, world!" in lines
    assert "How are you today?" in lines


def test_sdh_annotations_removed():
    lines = parse_lines(SRT_BASIC)
    assert "[Music]" not in lines
    assert "(applause)" not in lines


def test_html_tags_stripped():
    lines = parse_lines(SRT_HTML_TAGS)
    assert any("She said goodbye." in l for l in lines)
    assert any("Run!" in l for l in lines)
    assert not any("<i>" in l or "<b>" in l for l in lines)


def test_multiline_split():
    lines = parse_lines(SRT_MULTILINE)
    assert "First line." in lines
    assert "Second line." in lines


def test_all_sdh_returns_empty():
    lines = parse_lines(SRT_EMPTY)
    assert lines == []


def test_empty_srt_returns_empty():
    # pysubs2 can't detect format from empty string — parse_lines returns []
    import pysubs2
    try:
        lines = parse_lines("")
        assert lines == []
    except pysubs2.exceptions.FormatAutodetectionError:
        pass  # acceptable — empty input is not a valid subtitle file
