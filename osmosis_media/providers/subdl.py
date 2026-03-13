import io
import os
import zipfile

import httpx

from osmosis_media.providers.base import SubtitleResult

_API = "https://api.subdl.com/api/v1/subtitles"
_DL = "https://dl.subdl.com"


class SubDLProvider:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("SUBDL_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "SubDL API key required. Pass api_key= or set SUBDL_API_KEY env var."
            )

    async def search(
        self,
        title: str,
        language: str,
        season: int | None = None,
        episode: int | None = None,
    ) -> list[SubtitleResult]:
        params: dict = {
            "api_key": self.api_key,
            "film_name": title,
            "languages": language.upper(),
            "subs_per_page": 10,
        }
        if season is not None:
            params["type"] = "tv"
            params["season_number"] = season
            if episode is not None:
                params["episode_number"] = episode
        else:
            params["type"] = "movie"

        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(_API, params=params)
            r.raise_for_status()
            data = r.json()

        return [
            SubtitleResult(
                name=s.get("name", ""),
                url=s["url"],
                lang=s.get("lang", language),
            )
            for s in data.get("subtitles", [])
        ]

    async def download(self, result: SubtitleResult) -> str:
        url = f"{_DL}{result.url}"
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            r = await client.get(url)
            r.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
            srt_names = [n for n in zf.namelist() if n.lower().endswith(".srt")]
            if not srt_names:
                raise ValueError(f"No SRT file found in ZIP from {result.name!r}")
            # Prefer the shortest name (usually the clean one, not a subfolder path)
            srt_names.sort(key=len)
            return zf.read(srt_names[0]).decode("utf-8", errors="replace")
