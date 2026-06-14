"""Doodstream extractor.

Verified live. AniWorld's ``/redirect/<id>`` lands on a Doodstream mirror
(currently ``playmogo.com``) whose embed page contains::

    $.get('/pass_md5/<path>/<token>', ...)
    function makePlay() { ... return <random10> + "?token=<token>&expiry=" + Date.now(); }

Resolution: GET the ``/pass_md5/...`` path (with the embed page as Referer) to
obtain a base URL, then append a random 10-char string and the
``?token=...&expiry=<ms>`` query. The token is the final path segment.
"""

from __future__ import annotations

import random
import re
import string
import time
from urllib.parse import urlsplit

import requests

from .. import config
from ..models import Stream

_PASS_RE = re.compile(r"""\$\.get\(\s*['"](/pass_md5/[^'"]+)['"]""")
_ALPHABET = string.ascii_letters + string.digits


def parse_pass_md5(markup: str) -> tuple[str, str] | None:
    """Return ``(pass_md5_path, token)`` from the embed markup (offline-testable)."""
    match = _PASS_RE.search(markup)
    if not match:
        return None
    path = match.group(1)
    token = path.rstrip("/").rsplit("/", 1)[-1]
    if not token:
        return None
    return path, token


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


def _random_suffix(length: int = 10) -> str:
    return "".join(random.choice(_ALPHABET) for _ in range(length))


def extract(embed_url: str, session: requests.Session) -> Stream | None:
    try:
        resp = session.get(
            embed_url,
            timeout=config.TIMEOUT,
            headers={"Referer": config.BASE_URL + "/"},
        )
        parsed = parse_pass_md5(resp.text)
        if not parsed:
            return None
        path, token = parsed
        host = _origin(resp.url)
        base = session.get(
            host + path,
            timeout=config.TIMEOUT,
            headers={"Referer": resp.url},
        ).text.strip()
        if not base.startswith("http"):
            return None
        final = f"{base}{_random_suffix()}?token={token}&expiry={int(time.time() * 1000)}"
        return Stream(
            url=final,
            headers={
                "Referer": host + "/",
                "User-Agent": config.USER_AGENT,
            },
        )
    except (requests.RequestException, ValueError):
        return None
