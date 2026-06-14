"""Language-selection logic: available_languages + language-restricted ordering."""

from __future__ import annotations

from aniworld_cli import config
from aniworld_cli.models import Hoster
from aniworld_cli.resolve import available_languages, order_hosters


def _h(name, lang):
    return Hoster(name=name, lang_key=0, lang=lang, redirect_url=f"/redirect/{name}-{lang}")


def test_available_languages_ordered_by_priority(monkeypatch):
    monkeypatch.delenv("ANIWORLD_LANG", raising=False)
    hosters = [
        _h("VOE", config.LANG_ENG_SUB),
        _h("Vidmoly", config.LANG_GER_DUB),
        _h("VOE", config.LANG_GER_SUB),
        _h("Doodstream", config.LANG_GER_DUB),  # duplicate language
    ]
    assert available_languages(hosters) == [
        config.LANG_GER_DUB,
        config.LANG_GER_SUB,
        config.LANG_ENG_SUB,
    ]


def test_available_languages_keeps_unknown_last(monkeypatch):
    monkeypatch.delenv("ANIWORLD_LANG", raising=False)
    hosters = [_h("VOE", "lang-9"), _h("VOE", config.LANG_GER_DUB)]
    langs = available_languages(hosters)
    assert langs[0] == config.LANG_GER_DUB
    assert langs[-1] == "lang-9"


def test_order_restricts_to_chosen_language(monkeypatch):
    monkeypatch.delenv("ANIWORLD_HOSTER", raising=False)
    hosters = [
        _h("VOE", config.LANG_GER_DUB),
        _h("Vidmoly", config.LANG_GER_SUB),
        _h("Filemoon", config.LANG_GER_SUB),
        _h("VOE", config.LANG_GER_SUB),
    ]
    ordered = order_hosters(hosters, language=config.LANG_GER_SUB)
    assert {h.lang for h in ordered} == {config.LANG_GER_SUB}
    # Within the chosen language, hoster priority applies: VOE before Filemoon.
    names = [h.name for h in ordered]
    assert names.index("VOE") < names.index("Filemoon")


def test_order_language_allows_unknown_token():
    hosters = [_h("VOE", "lang-9"), _h("VOE", "ger-dub")]
    ordered = order_hosters(hosters, language="lang-9")
    assert len(ordered) == 1 and ordered[0].lang == "lang-9"
