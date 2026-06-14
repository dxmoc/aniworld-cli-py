"""Central configuration.

Values here are intentionally easy to override. Anything that is known to be
volatile on the live site (language keys, markup-specific selectors) lives next
to its parser, not here.
"""

from __future__ import annotations

import os

# Base host. Verified reachable before any parser relies on it (see search.py).
BASE_URL = os.environ.get("ANIWORLD_BASE_URL", "https://aniworld.to")

# A realistic, current desktop browser User-Agent. The site is behind anti-bot
# tooling; a plausible UA reduces friction.
USER_AGENT = os.environ.get(
    "ANIWORLD_UA",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
)

# HTTP behaviour.
CONNECT_TIMEOUT = 10.0
READ_TIMEOUT = 20.0
TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.6  # seconds; grows per retry
# Polite delay between sequential requests so we do not hammer the site.
REQUEST_DELAY = 0.4

# Language priority. These are *our* canonical tokens; the mapping from the
# site's integer language keys to these tokens is discovered at runtime in
# episode.py, never hardcoded here.
LANG_GER_DUB = "ger-dub"
LANG_GER_SUB = "ger-sub"
LANG_ENG_SUB = "eng-sub"

DEFAULT_LANGUAGE_PRIORITY = [LANG_GER_DUB, LANG_GER_SUB, LANG_ENG_SUB]


def language_priority() -> list[str]:
    """Language priority, overridable via ANIWORLD_LANG (comma-separated)."""
    env = os.environ.get("ANIWORLD_LANG")
    if env:
        return [tok.strip() for tok in env.split(",") if tok.strip()]
    return list(DEFAULT_LANGUAGE_PRIORITY)


# Hoster priority. Matched case-insensitively against the names shown on the
# episode page. Try in order, fall through on failure.
DEFAULT_HOSTER_PRIORITY = [
    "VOE",
    "Filemoon",
    "Vidoza",
    "SpeedFiles",
    "Doodstream",
    "Vidmoly",
    "Streamtape",
]


def hoster_priority() -> list[str]:
    """Hoster priority, overridable via ANIWORLD_HOSTER (comma-separated)."""
    env = os.environ.get("ANIWORLD_HOSTER")
    if env:
        return [tok.strip() for tok in env.split(",") if tok.strip()]
    return list(DEFAULT_HOSTER_PRIORITY)
