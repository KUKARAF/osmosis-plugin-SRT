from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class SubtitleResult:
    name: str
    url: str
    lang: str


@runtime_checkable
class SubtitleProvider(Protocol):
    async def search(
        self,
        title: str,
        language: str,
        season: int | None,
        episode: int | None,
    ) -> list[SubtitleResult]: ...

    async def download(self, result: SubtitleResult) -> str: ...
