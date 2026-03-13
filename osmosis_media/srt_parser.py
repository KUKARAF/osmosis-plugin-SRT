import re

_SEQUENCE = re.compile(r"^\d+$")
_TIMESTAMP = re.compile(r"\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->")
_HTML_TAG = re.compile(r"<[^>]+>")
_ASS_TAG = re.compile(r"\{[^}]+\}")  # ASS/SSA override tags like {\an8}
_SDH_NOTE = re.compile(r"^\[.*?\]$|^\(.*?\)$")  # [Music] (applause)


def parse_lines(srt: str) -> list[str]:
    """
    Strip SRT formatting and return clean dialogue lines.

    Removes: sequence numbers, timestamps, HTML/ASS tags, SDH annotations.
    Preserves: the actual spoken dialogue text.
    """
    lines = []
    for line in srt.splitlines():
        line = line.strip()
        if not line:
            continue
        if _SEQUENCE.match(line):
            continue
        if _TIMESTAMP.search(line):
            continue
        line = _HTML_TAG.sub("", line)
        line = _ASS_TAG.sub("", line)
        line = line.strip()
        if not line:
            continue
        if _SDH_NOTE.match(line):
            continue
        lines.append(line)
    return lines
