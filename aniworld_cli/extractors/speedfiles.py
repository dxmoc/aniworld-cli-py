"""speedfiles extractor (placeholder).

Not currently served by AniWorld: a live survey across multiple series found only
VOE, Doodstream, Filemoon and Vidmoly. Per the extractor contract this returns
None so the resolver falls through. Implementing it properly requires a live
embed fixture to verify against (the brief forbids guessing volatile values), so
it is intentionally left unimplemented until speedfiles reappears on the site.
"""

from __future__ import annotations

import requests

from ..models import Stream


def extract(embed_url: str, session: requests.Session) -> Stream | None:
    """Return None until a live speedfiles embed fixture is available."""
    return None
