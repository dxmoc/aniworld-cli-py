"""Shared HTTP session: realistic UA, timeouts, retry/backoff, polite delay."""

from __future__ import annotations

import time

import requests
from requests.adapters import HTTPAdapter

try:  # urllib3 is a requests dependency; import path differs across versions
    from urllib3.util.retry import Retry
except ImportError:  # pragma: no cover
    from requests.packages.urllib3.util.retry import Retry  # type: ignore

from . import config


class CloudflareChallenge(Exception):
    """Raised when a response looks like a Cloudflare anti-bot challenge."""


_session: requests.Session | None = None
_last_request_at = 0.0


def get_session() -> requests.Session:
    """Return the process-wide session, creating it on first use."""
    global _session
    if _session is None:
        s = requests.Session()
        s.headers.update(
            {
                "User-Agent": config.USER_AGENT,
                "Accept-Language": "de-DE,de;q=0.9,en;q=0.6",
            }
        )
        retry = Retry(
            total=config.MAX_RETRIES,
            backoff_factor=config.BACKOFF_FACTOR,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        _session = s
    return _session


def _throttle() -> None:
    """Keep a small minimum gap between requests."""
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    wait = config.REQUEST_DELAY - elapsed
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _looks_like_cloudflare(resp: requests.Response) -> bool:
    if resp.status_code not in (403, 503):
        return False
    server = resp.headers.get("Server", "").lower()
    body = resp.text[:4000].lower()
    markers = ("just a moment", "cf-chl", "challenge-platform", "cf-browser-verification")
    return "cloudflare" in server and any(m in body for m in markers)


def get(url: str, **kwargs: object) -> requests.Response:
    """GET with throttle, shared session, and Cloudflare detection."""
    _throttle()
    kwargs.setdefault("timeout", config.TIMEOUT)
    resp = get_session().get(url, **kwargs)  # type: ignore[arg-type]
    if _looks_like_cloudflare(resp):
        raise CloudflareChallenge(url)
    return resp


def post(url: str, **kwargs: object) -> requests.Response:
    """POST with throttle, shared session, and Cloudflare detection."""
    _throttle()
    kwargs.setdefault("timeout", config.TIMEOUT)
    resp = get_session().post(url, **kwargs)  # type: ignore[arg-type]
    if _looks_like_cloudflare(resp):
        raise CloudflareChallenge(url)
    return resp
