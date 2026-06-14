"""M2 search parser tests — offline against a saved fixture (no network)."""

from __future__ import annotations

import json
from pathlib import Path

from aniworld_cli import config
from aniworld_cli.search import parse

FIXTURE = Path(__file__).parent / "fixtures" / "search_naruto.json"


def _payload():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_parse_keeps_only_series_roots():
    series = parse(_payload())
    assert series, "expected at least one series"
    for s in series:
        # 3 path segments after the host: anime/stream/<slug>
        assert s.url.startswith(config.BASE_URL + "/anime/stream/")
        assert s.url.count("/staffel-") == 0
        assert s.url.count("/episode-") == 0


def test_parse_strips_markup_and_dedupes():
    series = parse(_payload())
    slugs = [s.slug for s in series]
    assert len(slugs) == len(set(slugs)), "slugs must be unique"
    naruto = next(s for s in series if s.slug == "naruto")
    assert naruto.title == "Naruto"  # <em> tags stripped
    assert "&" not in naruto.title  # entities decoded


def test_parse_decodes_entities_in_title():
    series = parse(_payload())
    spinoff = next(s for s in series if s.slug == "naruto-spin-off-rock-lee-his-ninja-pals")
    assert spinoff.title == "Naruto Spin-Off: Rock Lee & His Ninja Pals"


def test_parse_handles_garbage():
    assert parse([]) == []
    assert parse([{"link": "/support/frage/x", "title": "x"}]) == []
    assert parse([{"foo": "bar"}]) == []
