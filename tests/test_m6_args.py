"""M6 tests: --episode parsing and argparse wiring (no network)."""

from __future__ import annotations

from aniworld_cli.__main__ import build_parser
from aniworld_cli.cli import parse_episode_arg


def test_parse_episode_arg_valid():
    assert parse_episode_arg("1-3") == (1, 3)
    assert parse_episode_arg("0-1") == (0, 1)  # films
    assert parse_episode_arg("12-345") == (12, 345)


def test_parse_episode_arg_invalid():
    assert parse_episode_arg("1") is None
    assert parse_episode_arg("a-b") is None
    assert parse_episode_arg("1-2-3") is None
    assert parse_episode_arg("") is None


def test_parser_defaults():
    args = build_parser().parse_args([])
    assert args.query is None
    assert args.debug is False
    assert args.no_menu is False


def test_parser_full():
    args = build_parser().parse_args(
        ["naruto", "--episode", "1-1", "--no-menu", "--debug", "--lang", "eng-sub"]
    )
    assert args.query == "naruto"
    assert args.episode == "1-1"
    assert args.no_menu is True
    assert args.debug is True
    assert args.lang == "eng-sub"
