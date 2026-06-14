"""VOE extractor.

Verified live. The ``/redirect/<id>`` link 301s to ``https://voe.sx/e/<code>``,
which serves a tiny JS stub that bounces to a rotating mirror domain
(``window.location.href = 'https://<mirror>/e/<code>'``). The mirror's embed page
embeds the stream inside a ``<script type="application/json">["..."]</script>``
blob, obfuscated with this reversible pipeline:

    rot13  ->  strip junk pairs  ->  base64 decode  ->  shift each byte by -3
    ->  reverse  ->  base64 decode  ->  JSON

The resulting object exposes ``source`` (HLS ``master.m3u8``, preferred) and
``direct_access_url`` (progressive mp4, fallback).
"""

from __future__ import annotations

import base64
import codecs
import json
import re
from urllib.parse import urlsplit

import requests

from .. import config
from ..models import Stream

_JSON_RE = re.compile(
    r'<script[^>]+type="application/json"[^>]*>(.*?)</script>', re.S
)
_REDIRECT_RE = re.compile(r"""window\.location\.href\s*=\s*['"]([^'"]+)['"]""")
_JUNK_PAIRS = ("@$", "^^", "~@", "%?", "*~", "!!", "#&")


def _decode_blob(blob: str) -> dict | None:
    """Apply VOE's reversible obfuscation pipeline to one JSON-array string."""
    try:
        outer = json.loads(blob)
        s = outer[0] if isinstance(outer, list) else outer
        s = codecs.decode(s, "rot_13")
        for pair in _JUNK_PAIRS:
            s = s.replace(pair, "")
        s = base64.b64decode(s).decode("utf-8")
        s = "".join(chr(ord(c) - 3) for c in s)[::-1]
        s = base64.b64decode(s).decode("utf-8")
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except (ValueError, IndexError, UnicodeDecodeError):
        return None


def parse_embed(markup: str) -> str | None:
    """Extract the final stream URL from a VOE embed page (offline-testable)."""
    match = _JSON_RE.search(markup)
    if not match:
        return None
    obj = _decode_blob(match.group(1).strip())
    if not obj:
        return None
    return obj.get("source") or obj.get("direct_access_url") or None


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


def extract(embed_url: str, session: requests.Session) -> Stream | None:
    try:
        resp = session.get(embed_url, timeout=config.TIMEOUT)
        # Follow the JS bounce to the mirror domain (at most a couple of hops).
        for _ in range(3):
            hop = _REDIRECT_RE.search(resp.text)
            if not hop:
                break
            resp = session.get(
                hop.group(1),
                timeout=config.TIMEOUT,
                headers={"Referer": _origin(resp.url)},
            )
        stream_url = parse_embed(resp.text)
        if not stream_url:
            return None
        return Stream(
            url=stream_url,
            headers={
                "Referer": _origin(resp.url),
                "User-Agent": config.USER_AGENT,
            },
        )
    except (requests.RequestException, ValueError):
        return None
