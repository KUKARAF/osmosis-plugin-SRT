import re

import pysubs2

_SDH_NOTE = re.compile(r"^\[.*?\]$|^\(.*?\)$")  # [Music] (applause)
# Raw ASS metadata that leaks through when pysubs2 mis-detects the format
_ASS_METADATA = re.compile(r"^(Dialogue|Comment|Format|Style)\s*:", re.IGNORECASE)
# ASS timestamps like 0:00:34.47 — if present, the line is metadata not dialogue
_ASS_TIMESTAMP = re.compile(r"\d:\d{2}:\d{2}\.\d{2}")
# ASS section headers
_ASS_SECTION = re.compile(r"^\[.+\]\s*$")
# ASS hard-newline markers and inline override tags
_ASS_NEWLINE = re.compile(r"\\[Nn]")
_ASS_TAGS = re.compile(r"\{\\[^}]*\}")
# Style/name patterns that indicate sign, title card, or non-dialogue overlay events.
# Matches fansub conventions: Cart_*, cartel, sign, OP/ED karaoke, typesetting, etc.
_SIGN_STYLE = re.compile(
    r"(?i)sign|cartel|cart_|typeset|caption|credit|karaoke|kfx|romaji|op_|ed_|"
    r"^(?:op|ed)$|title(?!_default)"
)


def _detect_format(content: str) -> str | None:
    """Best-effort format hint to help pysubs2 when auto-detect fails."""
    head = content.lstrip("\ufeff").lstrip()[:500]
    if "[Script Info]" in head or "[V4" in head:
        return "ass"
    if head.startswith("WEBVTT"):
        return "vtt"
    return None


def parse_lines(srt: str) -> list[str]:
    """
    Strip subtitle formatting and return clean dialogue lines.

    Auto-detects SRT, ASS/SSA, and VTT via pysubs2.
    Removes: inline tags, comments, SDH annotations.
    Preserves: the actual spoken dialogue text.
    """
    fmt = _detect_format(srt)
    kwargs = {"format_": fmt} if fmt else {}
    subs = pysubs2.SSAFile.from_string(srt, **kwargs)
    lines = []
    for event in subs:
        if event.is_comment:
            continue
        # Skip sign/cartel/title-card events (non-dialogue overlays common in ASS fansubs)
        if _SIGN_STYLE.search(event.style) or _SIGN_STYLE.search(event.name):
            continue
        text = event.plaintext.strip()
        if not text:
            continue
        # Clean residual ASS formatting that plaintext may miss
        text = _ASS_NEWLINE.sub("\n", text)
        text = _ASS_TAGS.sub("", text)
        for line in text.split("\n"):
            line = line.strip()
            if not line or _SDH_NOTE.match(line):
                continue
            # Skip raw ASS metadata lines (format mis-detection fallback)
            if _ASS_METADATA.match(line):
                continue
            if _ASS_TIMESTAMP.search(line):
                continue
            if _ASS_SECTION.match(line):
                continue
            lines.append(line)
    return lines
