"""vidmoly extractor. Implemented in a later milestone (M4 VOE first, then M5)."""

from __future__ import annotations

import requests

from ..models import Stream


def extract(embed_url: str, session: requests.Session) -> Stream | None:
    """Resolve the final stream for a vidmoly embed page.

    Returns Stream(url, headers) on success or None on failure.
    """
    # TODO(milestone): implement against a saved live fixture.
    return None
