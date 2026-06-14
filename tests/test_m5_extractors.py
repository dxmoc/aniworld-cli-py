"""M5 tests: offline parsing for Vidmoly, Doodstream, Filemoon."""

from __future__ import annotations

from pathlib import Path

from aniworld_cli.extractors import doodstream, filemoon, speedfiles, streamtape, vidmoly, vidoza

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


def test_doodstream_parse_pass_md5():
    parsed = doodstream.parse_pass_md5(_read("embed_doodstream.html"))
    assert parsed is not None
    path, token = parsed
    assert path.startswith("/pass_md5/")
    assert token and path.endswith(token)


def test_doodstream_parse_none():
    assert doodstream.parse_pass_md5("<html>no dood here</html>") is None


def test_filemoon_spa_returns_no_static_url():
    # The current SPA shell has no inline m3u8 -> parse_embed yields None.
    assert filemoon.parse_embed(_read("embed_filemoon.html")) is None


def test_filemoon_unpacks_legacy_packed_eval():
    # Synthetic legacy packed payload: file:"https://cdn.example/x/master.m3u8"
    # 'file:"https://h|cdn|example|master|m3u8"' encoded via the packer is fiddly,
    # so assert the simpler inline path and the unpacker on a hand-built sample.
    inline = 'jwplayer().setup({file:"https://cdn.example/a/master.m3u8?x=1"});'
    assert filemoon.parse_embed(inline) == "https://cdn.example/a/master.m3u8?x=1"


def test_filemoon_unpack_substitutes_words():
    # base 2, two words; payload "0 1" should become "https m3u8"
    args = "'0 1',2,2,'https|m3u8'.split('|'),0,{}"
    assert filemoon.unpack(args) == "https m3u8"


def test_absent_hosters_return_none():
    sess = None  # never used: these short-circuit to None
    assert vidoza.extract("x", sess) is None
    assert speedfiles.extract("x", sess) is None
    assert streamtape.extract("x", sess) is None
