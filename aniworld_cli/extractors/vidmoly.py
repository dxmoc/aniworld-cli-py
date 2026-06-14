"""Vidmoly extractor.

Verified live. The ``/redirect/<id>`` lands directly on a Vidmoly embed page
(``vidmoly.*/embed-<code>.html``) that sets up jwplayer inline with::

    sources: [{ file: 'https://.../master.m3u8?...' }]

We read that ``file`` value straight out of the markup.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

import requests

from .. import config
from ..models import Stream

_SOURCES_RE = re.compile(
    r"""sources\s*:\s*\[\s*\{\s*file\s*:\s*["']([^"']+)["']""", re.S
)


def parse_embed(markup: str) -> str | None:
    """Extract the jwplayer source URL (offline-testable)."""
    match = _SOURCES_RE.search(markup)
    return match.group(1) if match else None


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


def extract(embed_url: str, session: requests.Session) -> Stream | None:
    try:
        resp = session.get(
            embed_url,
            timeout=config.TIMEOUT,
            headers={"Referer": config.BASE_URL + "/"},
        )
        url = parse_embed(resp.text)
        if not url:
            return None
        return Stream(
            url=url,
            headers={
                "Referer": _origin(resp.url) + "/",
                "User-Agent": config.USER_AGENT,
            },
        )
    except (requests.RequestException, ValueError):
        return None
