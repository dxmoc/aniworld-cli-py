"""All user-facing strings. German only.

Keep every German string here so the rest of the code stays English. Use ``t``
for lookups; values may contain ``{}`` placeholders for ``str.format``.
"""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # Generic
    "app_tagline": "aniworld-cli – Streaming über mpv",
    "goodbye": "Tschüss!",
    "aborted": "Abgebrochen.",
    "unexpected_error": "Unerwarteter Fehler. Mehr Details mit --debug.",
    # Search
    "search_prompt": "Suche:",
    "searching": "Suche läuft …",
    "no_results": "Keine Treffer für „{}“.",
    "choose_series": "Serie wählen:",
    # Seasons / episodes
    "loading_series": "Lade Serieninformationen …",
    "choose_season": "Staffel wählen:",
    "choose_episode": "Folge wählen:",
    "season_label": "Staffel {}",
    "movies_label": "Filme",
    "no_episodes": "Keine Folgen gefunden.",
    # Language selection
    "choose_language": "Sprache / Untertitel wählen:",
    "lang_ger-dub": "Deutsch (Dub)",
    "lang_ger-sub": "Original mit deutschem Untertitel (Ger-Sub)",
    "lang_eng-sub": "Original mit englischem Untertitel (Eng-Sub)",
    # Hoster / extraction
    "loading_hosters": "Lade Hoster …",
    "no_hosters": "Keine passenden Hoster gefunden.",
    "resolving_hoster": "Löse Hoster „{}“ auf …",
    "extract_failed": "Hoster „{}“ konnte nicht aufgelöst werden, versuche nächsten …",
    "stream_dead": "Stream von „{}“ nicht abspielbar (z. B. 403), versuche nächsten …",
    "all_hosters_failed": "Kein Hoster lieferte einen abspielbaren Stream.",
    "resolved_stream": "Stream gefunden über „{}“.",
    # Player
    "mpv_missing": "mpv wurde nicht gefunden.",
    "mpv_hint_linux": "Installation (Linux): „sudo pacman -S mpv“ / „sudo apt install mpv“ / „sudo dnf install mpv“.",
    "mpv_hint_windows": "Installation (Windows): „scoop install mpv“ oder „winget install mpv“.",
    "starting_player": "Starte mpv …",
    "player_error": "mpv konnte nicht gestartet werden.",
    # Post-playback menu
    "what_next": "Was nun?",
    "next_episode": "Nächste Folge",
    "other_episode": "Andere Folge",
    "quit": "Beenden",
    "no_next_episode": "Keine weitere Folge in dieser Staffel.",
    "now_playing": "Spiele: {}",
    # Resume / watchlist / auto mode
    "resume_prompt": "Fortsetzen?",
    "resume_continue": "Weiter bei {}",
    "resume_choose_other": "Andere Folge wählen",
    "choose_from_watchlist": "Aus deiner Watchlist wählen:",
    "watchlist_entry": "{} – zuletzt {}",
    "watchlist_empty": "Deine Watchlist ist leer – schau erst etwas an, dann merke ich es mir.",
    "auto_next": "Auto-Modus: nächste Folge …",
    "auto_season_end": "Staffelende erreicht – Auto-Modus beendet.",
    # Argument handling
    "episode_arg_invalid": "Ungültiges Format für --episode: „{}“. Erwartet: Staffel-Folge, z. B. 1-3 (oder 0-1 für Filme).",
    "episode_not_found": "Folge {} nicht gefunden.",
    "season_not_found": "Staffel {} nicht gefunden.",
    "no_query": "Kein Suchbegriff angegeben.",
    # Network / anti-bot
    "network_error": "Netzwerkfehler. Ist die Seite erreichbar?",
    "cloudflare_block": (
        "Die Seite ist hinter einem Cloudflare-Schutz. "
        "Optional hilft ein externer „flaresolverr“-Dienst (nicht enthalten)."
    ),
    # Debug
    "debug_stream_url": "Stream-URL: {}",
    "debug_headers": "Header: {}",
}


def t(key: str, *args: object) -> str:
    """Look up a German string and optionally ``format`` it."""
    text = STRINGS.get(key, key)
    if args:
        return text.format(*args)
    return text
