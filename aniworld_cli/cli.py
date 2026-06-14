"""Interactive flow (questionary menus), German UX.

Drives the whole pipeline: search -> series -> season/episode -> resolve a stream
by language+hoster priority -> mpv. After playback it offers a
"Nächste Folge / Andere Folge / Beenden" loop. ``--no-menu`` and ``--episode``
allow a fully non-interactive run; ``--debug`` resolves and prints the final URL
without launching mpv.
"""

from __future__ import annotations

import argparse

import questionary

from . import i18n, player
from .models import Episode, Series, Stream

# A navigation position: the chosen season, its episode list, and the index
# of the current episode within that list.
Nav = tuple[int, list[Episode], int]


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


def _season_label(season: int) -> str:
    return i18n.t("movies_label") if season == 0 else i18n.t("season_label", season)


def parse_episode_arg(value: str) -> tuple[int, int] | None:
    """Parse ``--episode S-E`` into ``(season, number)``. ``0-N`` == film N."""
    parts = value.split("-")
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def _resolve_query(args: argparse.Namespace) -> str | None:
    query = args.query
    if not query and not args.no_menu:
        query = questionary.text(i18n.t("search_prompt")).ask()
    return query.strip() if query else None


def _pick_series(results: list[Series], args: argparse.Namespace) -> Series | None:
    if args.no_menu:
        return results[0]
    return _select(  # type: ignore[return-value]
        i18n.t("choose_series"),
        [questionary.Choice(s.display, value=s) for s in results],
    )


def choose_episode_nav(series: Series) -> Nav | None:
    """Interactive season -> episode selection, returning a Nav position."""
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

    chosen = _select(
        i18n.t("choose_episode"),
        [questionary.Choice(e.label, value=i) for i, e in enumerate(episodes)],
    )
    if chosen is None:
        return None
    return season, episodes, chosen


def _initial_nav(series: Series, args: argparse.Namespace) -> Nav | None:
    """Decide the first episode: from --episode, from --no-menu defaults, or menu."""
    from . import series as series_mod

    if args.episode:
        parsed = parse_episode_arg(args.episode)
        if not parsed:
            print(i18n.t("episode_arg_invalid", args.episode))
            return None
        season, number = parsed
        seasons = series_mod.list_seasons(series)
        if season not in seasons:
            print(i18n.t("season_not_found", season))
            return None
        episodes = series_mod.list_episodes(series, season)
        for idx, ep in enumerate(episodes):
            if ep.number == number:
                return season, episodes, idx
        print(i18n.t("episode_not_found", number))
        return None

    if args.no_menu:
        seasons = series_mod.list_seasons(series)
        if not seasons:
            print(i18n.t("no_episodes"))
            return None
        # Prefer the first real season over the films section when available.
        season = next((s for s in seasons if s != 0), seasons[0])
        episodes = series_mod.list_episodes(series, season)
        if not episodes:
            print(i18n.t("no_episodes"))
            return None
        return season, episodes, 0

    return choose_episode_nav(series)


def run(args: argparse.Namespace) -> int:
    """Top-level entry. Returns a process exit code."""
    print(i18n.t("app_tagline"))

    # mpv is required for actual playback (not for --debug).
    if not args.debug and not check_player(args.player):
        return 1

    query = _resolve_query(args)
    if not query:
        print(i18n.t("no_query") if args.no_menu else i18n.t("aborted"))
        return 0

    print(i18n.t("searching"))
    from . import search as search_mod

    results = search_mod.search(query)
    if not results:
        print(i18n.t("no_results", query))
        return 0

    series = _pick_series(results, args)
    if series is None:
        print(i18n.t("aborted"))
        return 0

    nav = _initial_nav(series, args)
    if nav is None:
        return 0
    return _playback_loop(series, nav, args)


def _playback_loop(series: Series, nav: Nav, args: argparse.Namespace) -> int:
    """Play the current episode, then offer next/other/quit until the user exits."""
    season, episodes, index = nav
    while True:
        episode = episodes[index]
        print(i18n.t("now_playing", episode.label))
        rc = resolve_and_play(episode, args)

        # Non-interactive modes play exactly one episode.
        if args.debug or args.no_menu:
            return rc

        action = post_playback_menu()
        if action in (None, "quit"):
            print(i18n.t("goodbye"))
            return 0
        if action == "next":
            if index + 1 < len(episodes):
                index += 1
            else:
                print(i18n.t("no_next_episode"))
        elif action == "other":
            new_nav = choose_episode_nav(series)
            if new_nav is None:
                print(i18n.t("goodbye"))
                return 0
            season, episodes, index = new_nav


def resolve_and_play(episode: Episode, args: argparse.Namespace) -> int:
    """Load hosters, resolve a stream by priority, then debug-print or play."""
    from . import episode as episode_mod
    from . import resolve as resolve_mod

    print(i18n.t("loading_hosters"))
    hosters = episode_mod.list_hosters(episode)
    if not hosters:
        print(i18n.t("no_hosters"))
        return 1

    stream, _hoster = resolve_mod.resolve_stream(hosters, report=print)
    if stream is None:
        print(i18n.t("all_hosters_failed"))
        return 1

    if args.debug:
        print(i18n.t("debug_stream_url", stream.url))
        print(i18n.t("debug_headers", stream.headers))
        return 0

    return play_stream(stream, args.player)


def post_playback_menu() -> str | None:
    """Shown after mpv exits: Nächste Folge / Andere Folge / Beenden."""
    return _select(  # type: ignore[return-value]
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
