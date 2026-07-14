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
from . import vidmoly, voe

ExtractFn = Callable[[str, requests.Session], Optional[Stream]]

# Keys are matched case-insensitively against hoster names from the episode page.
# Only hosters that actually resolve on the live site are registered; others
# (Doodstream, Filemoon, Vidoza, SpeedFiles, Streamtape) were dropped after they
# either added anti-bot gates or stopped being offered — see the README.
REGISTRY: dict[str, ExtractFn] = {
    "voe": voe.extract,
    "vidmoly": vidmoly.extract,
}


def dispatch(hoster_name: str) -> ExtractFn | None:
    """Return the extractor for ``hoster_name`` (case-insensitive), or None."""
    return REGISTRY.get(hoster_name.strip().lower())
