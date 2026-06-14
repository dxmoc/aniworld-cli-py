"""Pick and resolve a playable stream from a list of hosters.

Ordering follows the configured language priority first, then hoster priority,
so we exhaust the best available language's hosters before falling through to the
next language. Extraction failures fall through to the next candidate.
"""

from __future__ import annotations

from typing import Callable, Optional

from . import config, http, i18n
from .extractors import dispatch
from .models import Hoster, Stream


def available_languages(hosters: list[Hoster]) -> list[str]:
    """Distinct languages offered for an episode, ordered by config priority.

    Languages not in the configured priority are kept and appended at the end,
    so the user can still pick them from the menu.
    """
    pri = config.language_priority()
    uniq: list[str] = []
    for h in hosters:
        if h.lang not in uniq:
            uniq.append(h.lang)
    return sorted(uniq, key=lambda lang: pri.index(lang) if lang in pri else len(pri))


def order_hosters(hosters: list[Hoster], language: str | None = None) -> list[Hoster]:
    """Order hosters for resolution.

    If ``language`` is given, restrict to that exact language and order by hoster
    priority. Otherwise order by (language priority, hoster priority) and drop
    languages not in the configured priority.
    """
    host_pri = [h.lower() for h in config.hoster_priority()]

    def host_rank(h: Hoster) -> int:
        name = h.name.lower()
        return host_pri.index(name) if name in host_pri else len(host_pri)

    if language is not None:
        candidates = [h for h in hosters if h.lang == language]
        return sorted(candidates, key=host_rank)

    lang_pri = config.language_priority()

    def lang_rank(h: Hoster) -> int:
        return lang_pri.index(h.lang) if h.lang in lang_pri else len(lang_pri)

    candidates = [h for h in hosters if h.lang in lang_pri]
    return sorted(candidates, key=lambda h: (lang_rank(h), host_rank(h)))


def resolve_stream(
    hosters: list[Hoster],
    language: str | None = None,
    report: Optional[Callable[[str], None]] = None,
) -> tuple[Stream | None, Hoster | None]:
    """Try ordered hosters until one extractor yields a Stream.

    If ``language`` is given, only hosters of that language are tried. ``report``
    receives German status lines (defaults to no-op). Returns the resolved
    ``(Stream, Hoster)`` or ``(None, None)`` if all candidates fail.
    """
    say = report or (lambda _msg: None)
    session = http.get_session()
    for hoster in order_hosters(hosters, language):
        extract = dispatch(hoster.name)
        if extract is None:
            continue
        say(i18n.t("resolving_hoster", hoster.name))
        stream = extract(hoster.redirect_url, session)
        if stream is not None:
            say(i18n.t("resolved_stream", hoster.name))
            return stream, hoster
        say(i18n.t("extract_failed", hoster.name))
    return None, None
