"""Search: query -> list[Series].

Verified against the live site: ``POST /ajax/search`` with a ``keyword`` form
field returns a JSON array of ``{title, description, link}`` objects. The array
mixes series roots (``/anime/stream/<slug>``), episode-level hits
(``/anime/stream/<slug>/staffel-N/episode-M``) and unrelated support pages
(``/support/frage/...``). We keep only series roots and de-duplicate by slug.
"""

from __future__ import annotations

import html
import re

from . import config, http
from .models import Series

SEARCH_PATH = "/ajax/search"
_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    """Strip the ``<em>`` highlight tags and decode HTML entities."""
    return html.unescape(_TAG_RE.sub("", text or "")).strip()


def _is_series_root(link: str) -> bool:
    parts = [p for p in link.split("/") if p]
    return len(parts) == 3 and parts[0] == "anime" and parts[1] == "stream"


def _slug(link: str) -> str:
    return [p for p in link.split("/") if p][2]


def parse(payload: list[dict]) -> list[Series]:
    """Turn the raw JSON array into de-duplicated series. Offline-testable."""
    seen: set[str] = set()
    out: list[Series] = []
    for entry in payload:
        link = entry.get("link", "")
        if not _is_series_root(link):
            continue
        slug = _slug(link)
        if slug in seen:
            continue
        seen.add(slug)
        out.append(
            Series(
                title=_clean(entry.get("title", "")),
                slug=slug,
                url=config.BASE_URL + link,
                description=_clean(entry.get("description", "")),
            )
        )
    return out


def search(query: str) -> list[Series]:
    """Query the live AJAX search endpoint and return matching series."""
    query = (query or "").strip()
    if not query:
        return []
    resp = http.post(
        config.BASE_URL + SEARCH_PATH,
        data={"keyword": query},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    try:
        payload = resp.json()
    except ValueError:
        return []
    if not isinstance(payload, list):
        return []
    return parse(payload)
