"""M1 smoke tests: no network, pure unit checks."""

from __future__ import annotations

from aniworld_cli import config, i18n, player
from aniworld_cli.extractors import REGISTRY, dispatch
from aniworld_cli.models import Episode, Hoster, Series, Stream


def test_i18n_lookup_and_format():
    assert i18n.t("quit") == "Beenden"
    assert i18n.t("no_results", "naruto") == "Keine Treffer für „naruto“."
    # Unknown key falls back to the key itself.
    assert i18n.t("does_not_exist") == "does_not_exist"


def test_config_overrides(monkeypatch):
    monkeypatch.setenv("ANIWORLD_LANG", "eng-sub, ger-dub")
    assert config.language_priority() == ["eng-sub", "ger-dub"]
    monkeypatch.setenv("ANIWORLD_HOSTER", "VOE,Vidmoly")
    assert config.hoster_priority() == ["VOE", "Vidmoly"]


def test_default_priorities():
    assert config.DEFAULT_LANGUAGE_PRIORITY[0] == "ger-dub"
    assert config.DEFAULT_HOSTER_PRIORITY[0] == "VOE"


def test_registry_covers_priority_hosters():
    for name in config.DEFAULT_HOSTER_PRIORITY:
        assert dispatch(name) is not None, name
    assert set(REGISTRY) == {"voe", "vidmoly"}


def test_player_command_separates_user_agent():
    stream = Stream(
        url="https://cdn.example/video.m3u8",
        headers={"Referer": "https://voe.sx/", "User-Agent": "UA"},
    )
    cmd = player.build_command("mpv", stream)
    assert cmd[0] == "mpv"
    assert cmd[-1] == stream.url
    # User-Agent goes to its dedicated flag (avoids duplicate-header 400s)...
    assert "--user-agent=UA" in cmd
    # ...and must NOT be folded into --http-header-fields.
    hdr = next(a for a in cmd if a.startswith("--http-header-fields="))
    assert "Referer: https://voe.sx/" in hdr
    assert "User-Agent" not in hdr


def test_player_command_no_headers():
    cmd = player.build_command("mpv", Stream(url="https://x/y.mp4"))
    assert cmd == ["mpv", "https://x/y.mp4"]


def test_model_labels():
    ep = Episode(series_slug="s", url="u", season=1, number=3, title="X")
    assert ep.label == "S01E03 – X"
    movie = Episode(series_slug="s", url="u", season=0, number=2)
    assert movie.label == "Film 2"
    series = Series(title="Naruto", slug="naruto", url="u")
    assert series.display == "Naruto"
    h = Hoster(name="VOE", lang_key=1, lang="ger-dub", redirect_url="/redirect/1")
    assert h.name == "VOE"
