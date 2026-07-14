"""M9 tests: stream liveness check and hoster fallback (offline, fake session)."""

from __future__ import annotations

import requests

from aniworld_cli import resolve
from aniworld_cli.models import Hoster, Stream


class _Resp:
    def __init__(self, status: int, text: str = ""):
        self.status_code = status
        self.text = text

    def close(self):
        pass


class _FakeSession:
    """Maps exact URLs to canned responses; unknown URLs raise (like a 404-ish)."""

    def __init__(self, mapping: dict[str, _Resp], boom: bool = False):
        self.mapping = mapping
        self.boom = boom

    def get(self, url, **_kw):
        if self.boom:
            raise requests.ConnectionError("boom")
        if url not in self.mapping:
            return _Resp(404)
        return self.mapping[url]


_MASTER = "https://cdn/x/master.m3u8"
_VARIANT = "https://cdn/x/index.m3u8?t=1"
_SEGMENT = "https://cdn/x/seg0.ts"


def _hls_session(segment_status: int) -> _FakeSession:
    return _FakeSession(
        {
            _MASTER: _Resp(200, "#EXTM3U\nindex.m3u8?t=1\n"),
            _VARIANT: _Resp(200, "#EXTM3U\nseg0.ts\n"),
            _SEGMENT: _Resp(segment_status),
        }
    )


def test_hls_live_when_segment_ok():
    stream = Stream(url=_MASTER, headers={})
    assert resolve.stream_is_live(stream, _hls_session(200)) is True


def test_hls_dead_when_segment_403():
    stream = Stream(url=_MASTER, headers={})
    assert resolve.stream_is_live(stream, _hls_session(403)) is False


def test_progressive_live_and_dead():
    url = "https://cdn/video.mp4"
    assert resolve.stream_is_live(Stream(url=url), _FakeSession({url: _Resp(200)})) is True
    assert resolve.stream_is_live(Stream(url=url), _FakeSession({url: _Resp(403)})) is False


def test_network_error_is_not_live():
    assert resolve.stream_is_live(Stream(url=_MASTER), _FakeSession({}, boom=True)) is False


def test_resolve_falls_back_to_next_hoster_when_first_is_dead(monkeypatch):
    hosters = [
        Hoster(name="VOE", lang_key=1, lang="ger-dub", redirect_url="/redirect/voe"),
        Hoster(name="Vidmoly", lang_key=1, lang="ger-dub", redirect_url="/redirect/vid"),
    ]
    dead = Stream(url="voe-dead")
    live = Stream(url="vidmoly-live")

    def fake_dispatch(name):
        name = name.lower()
        if name == "voe":
            return lambda _url, _sess: dead
        if name == "vidmoly":
            return lambda _url, _sess: live
        return None

    monkeypatch.setattr(resolve, "dispatch", fake_dispatch)
    monkeypatch.setattr(resolve.http, "get_session", lambda: object())
    monkeypatch.setattr(resolve, "stream_is_live", lambda s, _sess: s.url != "voe-dead")

    stream, hoster = resolve.resolve_stream(hosters, language="ger-dub")
    assert stream is live
    assert hoster.name == "Vidmoly"


def test_verify_false_accepts_first_without_checking(monkeypatch):
    hosters = [Hoster(name="VOE", lang_key=1, lang="ger-dub", redirect_url="/r")]
    dead = Stream(url="voe-dead")
    monkeypatch.setattr(resolve, "dispatch", lambda _n: (lambda _u, _s: dead))
    monkeypatch.setattr(resolve.http, "get_session", lambda: object())

    def _boom(*_a, **_k):  # must NOT be called when verify=False
        raise AssertionError("liveness check ran despite verify=False")

    monkeypatch.setattr(resolve, "stream_is_live", _boom)
    stream, hoster = resolve.resolve_stream(hosters, language="ger-dub", verify=False)
    assert stream is dead
