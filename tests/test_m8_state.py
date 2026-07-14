"""M8 tests: persistent watch state + mpv media title (offline, no network)."""

from __future__ import annotations

import pytest

from aniworld_cli import player, state
from aniworld_cli.models import Episode, Series, Stream


@pytest.fixture(autouse=True)
def _isolate_state(tmp_path, monkeypatch):
    """Point the state store at a throwaway dir for every test."""
    monkeypatch.setenv("ANIWORLD_STATE_DIR", str(tmp_path))
    return tmp_path


def _series(slug: str = "naruto") -> Series:
    return Series(title="Naruto", slug=slug, url=f"https://x/anime/stream/{slug}")


def _episode(season: int, number: int) -> Episode:
    return Episode(series_slug="naruto", url="u", season=season, number=number, title="T")


def test_load_missing_returns_empty_skeleton():
    data = state.load()
    assert data["series"] == {}


def test_record_and_get_progress_roundtrip():
    state.record(_series(), _episode(3, 12))
    prog = state.get_progress("naruto")
    assert prog is not None
    assert prog["season"] == 3
    assert prog["number"] == 12
    assert prog["label"] == "S03E12 – T"
    assert prog["title"] == "Naruto"
    assert "updated" in prog


def test_record_overwrites_previous_point():
    state.record(_series(), _episode(1, 1))
    state.record(_series(), _episode(1, 2))
    prog = state.get_progress("naruto")
    assert prog["number"] == 2


def test_get_progress_unknown_is_none():
    assert state.get_progress("does-not-exist") is None


def test_list_entries_ordered_by_recency():
    # Write directly with explicit timestamps to control ordering deterministically.
    state.save(
        {
            "version": 1,
            "series": {
                "old": {"title": "Old", "url": "", "season": 1, "number": 1,
                        "label": "S01E01", "updated": "2026-01-01T00:00:00"},
                "new": {"title": "New", "url": "", "season": 1, "number": 5,
                        "label": "S01E05", "updated": "2026-07-01T00:00:00"},
            },
        }
    )
    entries = state.list_entries()
    assert [e["slug"] for e in entries] == ["new", "old"]


def test_list_series_returns_series_objects():
    state.record(_series("one-piece"), _episode(1, 1))
    series = state.list_series()
    assert len(series) == 1
    assert isinstance(series[0], Series)
    assert series[0].slug == "one-piece"


def test_remove_drops_series():
    state.record(_series(), _episode(1, 1))
    state.remove("naruto")
    assert state.get_progress("naruto") is None


def test_corrupt_file_is_treated_as_empty(_isolate_state):
    (_isolate_state / "state.json").write_text("{ not json", encoding="utf-8")
    assert state.load()["series"] == {}


def test_build_command_includes_media_title():
    stream = Stream(url="https://cdn/x.m3u8", headers={"Referer": "https://voe.sx/"})
    cmd = player.build_command("mpv", stream, title="Naruto – S03E12")
    assert "--force-media-title=Naruto – S03E12" in cmd
    assert cmd[-1] == stream.url  # URL stays last


def test_build_command_without_title_unchanged():
    stream = Stream(url="https://cdn/x.m3u8")
    assert player.build_command("mpv", stream) == ["mpv", "https://cdn/x.m3u8"]
