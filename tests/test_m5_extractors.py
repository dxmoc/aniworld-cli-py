"""M5 tests: offline parsing for the registered extractors (Vidmoly)."""

from __future__ import annotations

from pathlib import Path

from aniworld_cli.extractors import vidmoly

FIX = Path(__file__).parent / "fixtures"


def _read(name: str) -> str:
    return (FIX / name).read_text(encoding="utf-8")


def test_vidmoly_parse_embed():
    url = vidmoly.parse_embed(_read("embed_vidmoly.html"))
    assert url is not None
    assert url.endswith(".m3u8") or ".m3u8?" in url
    assert url.startswith("https://")


def test_vidmoly_parse_embed_none():
    assert vidmoly.parse_embed("<html>nothing</html>") is None