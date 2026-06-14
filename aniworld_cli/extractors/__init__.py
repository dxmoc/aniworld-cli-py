"""Extractor registry and dispatch.

Each extractor module exposes::

    def extract(embed_url: str, session: requests.Session) -> Stream | None

Returning a ``Stream`` on success, or ``None`` on any failure so the caller can
fall through to the next hoster by priority.
"""

from __future__ import annotations

from typing import Callable, Optional

import requests

from ..models import Stream
from . import doodstream, filemoon, speedfiles, streamtape, vidmoly, vidoza, voe

ExtractFn = Callable[[str, requests.Session], Optional[Stream]]

# Keys are matched case-insensitively against hoster names from the episode page.
REGISTRY: dict[str, ExtractFn] = {
    "voe": voe.extract,
    "filemoon": filemoon.extract,
    "vidoza": vidoza.extract,
    "speedfiles": speedfiles.extract,
    "doodstream": doodstream.extract,
    "vidmoly": vidmoly.extract,
    "streamtape": streamtape.extract,
}


def dispatch(hoster_name: str) -> ExtractFn | None:
    """Return the extractor for ``hoster_name`` (case-insensitive), or None."""
    return REGISTRY.get(hoster_name.strip().lower())
