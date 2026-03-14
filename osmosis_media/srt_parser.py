import re

import pysubs2

_SDH_NOTE = re.compile(r"^\[.*?\]$|^\(.*?\)$")  # [Music] (applause)


def parse_lines(srt: str) -> list[str]:
    """
    Strip subtitle formatting and return clean dialogue lines.

    Auto-detects SRT, ASS/SSA, and VTT via pysubs2.
    Removes: inline tags, comments, SDH annotations.
    Preserves: the actual spoken dialogue text.
    """
    subs = pysubs2.SSAFile.from_string(srt)
    lines = []
    for event in subs:
        if event.is_comment:
            continue
        text = event.plaintext.strip()
        if not text:
            continue
        for line in text.split("\n"):
            line = line.strip()
            if not line or _SDH_NOTE.match(line):
                continue
            lines.append(line)
    return lines
