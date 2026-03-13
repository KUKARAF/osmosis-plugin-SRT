from dataclasses import dataclass, field


@dataclass
class Word:
    lemma: str
    pos: str  # noun | verb | adj | adv | pron | prep | conj | other
    frequency: int
    forms: list[str] = field(default_factory=list)
    example: str | None = None
    cefr_hint: str | None = None

    def to_dict(self) -> dict:
        return {
            "lemma": self.lemma,
            "pos": self.pos,
            "frequency": self.frequency,
            "forms": self.forms,
            "example": self.example,
            "cefr_hint": self.cefr_hint,
        }


@dataclass
class MediaGoal:
    """
    Duck-typed output object. osmosis checks for title/language/media_type/words
    without importing this package.
    """
    title: str
    media_type: str  # movie | series | book | other
    language: str    # ISO 639-1
    words: list[Word]
    season: int | None = None
    episode: int | None = None
    raw_srt: str | None = None
    source_url: str | None = None
    word_count: int = 0
    unique_lemmas: int = 0

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "media_type": self.media_type,
            "language": self.language,
            "season": self.season,
            "episode": self.episode,
            "source_url": self.source_url,
            "word_count": self.word_count,
            "unique_lemmas": self.unique_lemmas,
            "words": [w.to_dict() for w in self.words],
        }
