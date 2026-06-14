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

    print(i18n.t("searching"))
    from . import search as search_mod

    results = search_mod.search(query)
    if not results:
        print(i18n.t("no_results", query))
        return 0

    series = _select(
        i18n.t("choose_series"),
        [questionary.Choice(s.display, value=s) for s in results],
    )
    if series is None:
        print(i18n.t("aborted"))
        return 0

    episode = choose_episode(series)
    if episode is None:
        print(i18n.t("aborted"))
        return 0

    return resolve_and_play(episode, args)


def resolve_and_play(episode, args: argparse.Namespace) -> int:
    """Load hosters, resolve a stream by priority, then debug-print or play."""
    from . import episode as episode_mod
    from . import resolve as resolve_mod

    print(i18n.t("loading_hosters"))
    hosters = episode_mod.list_hosters(episode)
    if not hosters:
        print(i18n.t("no_hosters"))
        return 0

    stream, _hoster = resolve_mod.resolve_stream(hosters, report=print)
    if stream is None:
        print(i18n.t("all_hosters_failed"))
        return 1

    if args.debug:
        print(i18n.t("debug_stream_url", stream.url))
        print(i18n.t("debug_headers", stream.headers))
        return 0

    return play_stream(stream, args.player)


def _season_label(season: int) -> str:
    return i18n.t("movies_label") if season == 0 else i18n.t("season_label", season)


def choose_episode(series):
    """Interactive season -> episode selection. Returns an Episode or None."""
    from . import series as series_mod

    print(i18n.t("loading_series"))
    seasons = series_mod.list_seasons(series)
    if not seasons:
        print(i18n.t("no_episodes"))
        return None

    season = _select(
        i18n.t("choose_season"),
        [questionary.Choice(_season_label(s), value=s) for s in seasons],
    )
    if season is None:
        return None

    episodes = series_mod.list_episodes(series, season)
    if not episodes:
        print(i18n.t("no_episodes"))
        return None

    return _select(
        i18n.t("choose_episode"),
        [questionary.Choice(e.label, value=e) for e in episodes],
    )


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
