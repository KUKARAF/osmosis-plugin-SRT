"""osmosis-media plugin — declares goal actions for media types."""
from __future__ import annotations


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
        ]

    async def on_startup(self, app):
        pass
