"""Interactive flow (questionary menus), German UX.

M1 wires the skeleton: tagline, mpv detection, a search prompt and the
post-playback menu shape. The data-fetching steps (search/seasons/episodes/
hosters/extraction) are filled in across M2–M5; until then they surface a
friendly German "not yet implemented" message instead of a traceback.
"""

from __future__ import annotations

import argparse

import questionary

from . import i18n, player
from .models import Stream


def _select(message: str, choices: list[questionary.Choice]) -> object | None:
    """Thin wrapper so Ctrl-C / empty selection returns None cleanly."""
    if not choices:
        return None
    return questionary.select(message, choices=choices).ask()


def check_player(player_path: str | None) -> str | None:
    """Locate mpv and, if missing, print a German install hint."""
    mpv = player.find_mpv(player_path)
    if not mpv:
        print(i18n.t("mpv_missing"))
        print(player.install_hint())
    return mpv


def run(args: argparse.Namespace) -> int:
    """Top-level interactive entry. Returns a process exit code."""
    print(i18n.t("app_tagline"))

    # mpv is required for actual playback (not for --debug).
    if not args.debug:
        if not check_player(args.player):
            return 1

    query = args.query
    if not query and not args.no_menu:
        query = questionary.text(i18n.t("search_prompt")).ask()
    if not query:
        print(i18n.t("aborted"))
        return 0

    # Pipeline below is built out in M2–M5. Keep the skeleton honest for now.
    print(i18n.t("searching"))
    try:
        from . import search as search_mod

        results = search_mod.search(query)
    except NotImplementedError as exc:
        print(f"[M1] {exc}")
        return 0

    if not results:
        print(i18n.t("no_results", query))
        return 0

    # Full season/episode/hoster/extract loop lands in M3–M6.
    print(i18n.t("no_hosters"))
    return 0


def post_playback_menu() -> str | None:
    """Shown after mpv exits: Nächste Folge / Andere Folge / Beenden."""
    return _select(
        i18n.t("what_next"),
        [
            questionary.Choice(i18n.t("next_episode"), value="next"),
            questionary.Choice(i18n.t("other_episode"), value="other"),
            questionary.Choice(i18n.t("quit"), value="quit"),
        ],
    )


def play_stream(stream: Stream, player_path: str | None) -> int:
    """Launch mpv, surfacing a German error if it cannot start."""
    print(i18n.t("starting_player"))
    try:
        return player.play(stream, player_path)
    except player.PlayerNotFound as exc:
        print(i18n.t("mpv_missing"))
        print(str(exc))
        return 1
