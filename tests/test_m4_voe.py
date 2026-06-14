"""M4 tests: VOE decode (offline fixture) + resolver ordering (pure)."""

from __future__ import annotations

from pathlib import Path

from aniworld_cli import config
from aniworld_cli.extractors import voe
from aniworld_cli.models import Hoster
from aniworld_cli.resolve import order_hosters

FIX = Path(__file__).parent / "fixtures"


def test_voe_parse_embed_yields_stream_url():
    markup = (FIX / "voe_mirror.html").read_text(encoding="utf-8")
    url = voe.parse_embed(markup)
    assert url is not None
    assert url.startswith("https://")
    # Prefers the HLS source for this fixture.
    assert ".m3u8" in url


def test_voe_parse_embed_handles_junk():
    assert voe.parse_embed("<html>no json here</html>") is None
    assert voe.parse_embed('<script type="application/json">["not-base64"]</script>') is None


def _h(name, lang):
    return Hoster(name=name, lang_key=0, lang=lang, redirect_url=f"/redirect/{name}")


def test_order_prefers_language_then_hoster(monkeypatch):
    monkeypatch.delenv("ANIWORLD_LANG", raising=False)
    monkeypatch.delenv("ANIWORLD_HOSTER", raising=False)
    hosters = [
        _h("Vidoza", config.LANG_GER_SUB),
        _h("VOE", config.LANG_ENG_SUB),
        _h("Filemoon", config.LANG_GER_DUB),
        _h("VOE", config.LANG_GER_DUB),
    ]
    ordered = order_hosters(hosters)
    # German dub first; within it, VOE outranks Filemoon.
    assert ordered[0].name == "VOE" and ordered[0].lang == config.LANG_GER_DUB
    assert ordered[1].name == "Filemoon" and ordered[1].lang == config.LANG_GER_DUB
    # Then ger-sub, then eng-sub.
    assert ordered[2].lang == config.LANG_GER_SUB
    assert ordered[3].lang == config.LANG_ENG_SUB


def test_order_drops_unknown_languages(monkeypatch):
    monkeypatch.delenv("ANIWORLD_LANG", raising=False)
    hosters = [_h("VOE", "lang-99"), _h("VOE", config.LANG_GER_DUB)]
    ordered = order_hosters(hosters)
    assert len(ordered) == 1
    assert ordered[0].lang == config.LANG_GER_DUB


def test_order_respects_lang_override(monkeypatch):
    monkeypatch.setenv("ANIWORLD_LANG", "eng-sub")
    hosters = [_h("VOE", config.LANG_GER_DUB), _h("VOE", config.LANG_ENG_SUB)]
    ordered = order_hosters(hosters)
    assert len(ordered) == 1
    assert ordered[0].lang == config.LANG_ENG_SUB
