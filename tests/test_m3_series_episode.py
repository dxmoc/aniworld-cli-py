"""M3 parser tests — offline against saved series/season/episode fixtures."""

from __future__ import annotations

from pathlib import Path

from aniworld_cli import config
from aniworld_cli.episode import parse_hosters, parse_language_map
from aniworld_cli.series import parse_episodes, parse_seasons

FIX = Path(__file__).parent / "fixtures"


def _read(name: str) -> str:
    return (FIX / name).read_text(encoding="utf-8")


def test_parse_seasons_includes_films_as_zero():
    seasons = parse_seasons(_read("series_naruto.html"), "naruto")
    assert seasons == [0, 1, 2, 3, 4]  # 0 == Filme, then staffel 1..4


def test_parse_episodes_staffel_one():
    eps = parse_episodes(_read("series_naruto.html"), "naruto", 1)
    assert eps, "expected episodes for season 1"
    assert eps[0].number == 1
    assert eps[0].season == 1
    assert eps[0].url.endswith("/anime/stream/naruto/staffel-1/episode-1")
    # strictly increasing, no dupes
    nums = [e.number for e in eps]
    assert nums == sorted(set(nums))
    assert eps[0].label == "S01E01"


def test_parse_episodes_films():
    eps = parse_episodes(_read("films_naruto.html"), "naruto", 0)
    assert eps, "expected film entries"
    assert all(e.season == 0 for e in eps)
    assert eps[0].url.endswith("/anime/stream/naruto/filme/film-1")
    assert eps[0].label.startswith("Film 1")


def test_language_map_derived_not_hardcoded():
    lang_map = parse_language_map(_read("episode_naruto_s1e1.html"))
    # We do not assume which integer means what; we assert the *derived* mapping
    # covers all three canonical tokens for this episode.
    assert set(lang_map.values()) >= {
        config.LANG_GER_DUB,
        config.LANG_GER_SUB,
        config.LANG_ENG_SUB,
    }


def test_parse_hosters():
    markup = _read("episode_naruto_s1e1.html")
    hosters = parse_hosters(markup)
    assert hosters, "expected hoster entries"
    names = {h.name for h in hosters}
    # VOE is present per the brief's priority list.
    assert "VOE" in names
    for h in hosters:
        assert h.redirect_url.startswith(config.BASE_URL + "/redirect/")
        assert h.lang in {
            config.LANG_GER_DUB,
            config.LANG_GER_SUB,
            config.LANG_ENG_SUB,
        } or h.lang.startswith("lang-")
