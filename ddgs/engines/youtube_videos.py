"""YouTube videos search engine implementation."""

import json
import logging
import re
from collections.abc import Generator, Mapping
from typing import Any, ClassVar
from urllib.parse import urlencode

from ddgs.base import BaseSearchEngine
from ddgs.results import VideosResult

logger = logging.getLogger(__name__)

YT_INITIAL_DATA_RE = re.compile(r"ytInitialData\s*=\s*(\{.*?\});", re.DOTALL)


def _pick_text(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if isinstance(value.get("simpleText"), str):
            return value["simpleText"]
        runs = value.get("runs")
        if isinstance(runs, list):
            return "".join(run.get("text", "") for run in runs if isinstance(run, dict)).strip()
    return ""


def _extract_yt_initial_data(html_text: str) -> dict[str, Any]:
    match = YT_INITIAL_DATA_RE.search(html_text)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except Exception as ex:  # noqa: BLE001
        logger.debug("Failed to parse ytInitialData: %r", ex)
        return {}


def _iter_video_renderers(obj: object) -> Generator[dict[str, Any], None, None]:
    if isinstance(obj, Mapping):
        video_renderer = obj.get("videoRenderer")
        if isinstance(video_renderer, Mapping):
            yield dict(video_renderer)
        for value in obj.values():
            yield from _iter_video_renderers(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _iter_video_renderers(value)


class YoutubeVideos(BaseSearchEngine[VideosResult]):
    """YouTube videos search engine."""

    name = "youtube"
    category = "videos"
    provider = "youtube"
    priority = 1.0

    search_url = "https://www.youtube.com/results"
    search_method = "GET"
    search_headers: ClassVar[dict[str, str]] = {
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
    }

    def build_payload(
        self,
        query: str,
        region: str,  # noqa: ARG002
        safesearch: str,  # noqa: ARG002
        timelimit: str | None,  # noqa: ARG002
        page: int = 1,  # noqa: ARG002
        **kwargs: str,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Build a payload for the YouTube search request."""
        return {"search_query": query}

    def extract_results(self, html_text: str) -> list[VideosResult]:
        """Extract video results from embedded ytInitialData JSON."""
        data = _extract_yt_initial_data(html_text)
        if not data:
            return []

        results = []
        for item in _iter_video_renderers(data):
            video_id = item.get("videoId")
            if not video_id:
                continue

            result = VideosResult()
            result.title = _pick_text(item.get("title"))
            result.description = _pick_text(item.get("descriptionSnippet"))
            result.duration = _pick_text(item.get("lengthText"))
            result.published = _pick_text(item.get("publishedTimeText"))
            result.uploader = _pick_text(item.get("ownerText"))
            result.publisher = result.uploader
            result.provider = self.provider
            result.content = f"https://www.youtube.com/watch?v={video_id}"
            result.embed_url = f"https://www.youtube.com/embed/{video_id}"

            thumbs = item.get("thumbnail", {}).get("thumbnails", [])
            if isinstance(thumbs, list):
                images = {str(i): thumb.get("url", "") for i, thumb in enumerate(thumbs) if isinstance(thumb, dict)}
                result.images = {k: v for k, v in images.items() if v}
            result.statistics = {"views": _pick_text(item.get("viewCountText"))}

            # Keep embed_html lightweight while still preserving a direct preview path.
            encoded = urlencode({"q": result.title or video_id})
            result.embed_html = (
                f'<iframe src="{result.embed_url}" title="{result.title}" loading="lazy"></iframe>'
                f"<!-- search:{encoded} -->"
            )
            results.append(result)

        return results
