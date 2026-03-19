"""osmosis-media plugin — declares goal actions for media types."""
from __future__ import annotations

from pathlib import Path


class MediaPlugin:
    name = "media"
    version = "0.1.0"

    def get_tools(self):
        return []

    def get_tool_handlers(self):
        return {}

    def get_router(self):
        return None

    def get_media_types(self):
        return ["series", "movie", "book"]

    def get_goal_actions(self):
        return [
            {
                "media_types": ["series", "movie"],
                "id": "import_subtitles",
                "label": "Import Vocab",
            },
            {
                "media_types": ["series", "movie", "book"],
                "id": "upload_subtitles",
                "label": "Upload SRT",
            },
        ]

    def get_prompts_dir(self):
        return None

    async def on_startup(self, app):
        pass
