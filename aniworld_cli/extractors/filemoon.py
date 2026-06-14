"""Filemoon extractor (best-effort).

Verified live: the current Filemoon (``filemoon.to``) serves a JavaScript SPA
("Byse Frontend") for both ``/d/`` and ``/e/`` paths and fetches the stream at
runtime via its own API — so it is *not* statically resolvable without executing
JS. When that is the case this extractor returns ``None`` and the resolver falls
through to the next hoster (per the brief's contract).

It still handles the older, statically-scrapable Filemoon embeds: a Dean-Edwards
``eval(function(p,a,c,k,e,d){...})`` packed block containing the ``.m3u8`` URL,
or a plain inline ``file:"...m3u8..."``. If Filemoon reverts to that form, this
keeps working.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

import requests

from .. import config
from ..models import Stream

_PACKED_RE = re.compile(
    r"eval\(function\(p,a,c,k,e,(?:d|r)\)\{.*?\}\((.*?)\)\)", re.S
)
_M3U8_RE = re.compile(r"""["'](https?://[^"']+?\.m3u8[^"']*)["']""")
_ARGS_RE = re.compile(
    r"""^\s*'(?P<p>.*)'\s*,\s*(?P<a>\d+)\s*,\s*(?P<c>\d+)\s*,\s*'(?P<k>.*?)'\.split\('\|'\)""",
    re.S,
)


def _unbase(n: int, base: int) -> str:
    """Encode ``n`` in the packer's base-``base`` alphabet (0-9a-z then A-Z)."""
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n == 0:
        return "0"
    out = ""
    while n > 0:
        out = digits[n % base] + out
        n //= base
    return out


def unpack(packed_args: str) -> str | None:
    """Reverse a Dean-Edwards p.a.c.k.e.d payload given its call arguments."""
    m = _ARGS_RE.search(packed_args)
    if not m:
        return None
    payload = m.group("p").replace("\\'", "'").replace("\\\\", "\\")
    base = int(m.group("a"))
    count = int(m.group("c"))
    words = m.group("k").split("|")

    mapping = {}
    for i in range(count):
        key = _unbase(i, base)
        mapping[key] = words[i] if i < len(words) and words[i] else key

    return re.sub(r"\b\w+\b", lambda mt: mapping.get(mt.group(0), mt.group(0)), payload)


def _embed_url(url: str) -> str:
    """Prefer the ``/e/`` embed path over the ``/d/`` download path."""
    return re.sub(r"/d/", "/e/", url, count=1)


def parse_embed(markup: str) -> str | None:
    """Extract an ``.m3u8`` URL from a (legacy) Filemoon embed (offline-testable)."""
    direct = _M3U8_RE.search(markup)
    if direct:
        return direct.group(1)
    packed = _PACKED_RE.search(markup)
    if packed:
        source = unpack(packed.group(1))
        if source:
            found = _M3U8_RE.search(source)
            if found:
                return found.group(1)
    return None


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


def extract(embed_url: str, session: requests.Session) -> Stream | None:
    try:
        target = _embed_url(embed_url)
        resp = session.get(
            target,
            timeout=config.TIMEOUT,
            headers={"Referer": config.BASE_URL + "/"},
            allow_redirects=True,
        )
        # The redirect chain ends at filemoon's own domain; re-fetch /e/ there.
        final = _embed_url(resp.url)
        if final != resp.url:
            resp = session.get(
                final,
                timeout=config.TIMEOUT,
                headers={"Referer": config.BASE_URL + "/"},
            )
        url = parse_embed(resp.text)
        if not url:
            return None  # SPA form: not statically resolvable -> fall through
        return Stream(
            url=url,
            headers={
                "Referer": _origin(resp.url) + "/",
                "User-Agent": config.USER_AGENT,
            },
        )
    except (requests.RequestException, ValueError):
        return None
