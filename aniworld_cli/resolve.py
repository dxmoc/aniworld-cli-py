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


def order_hosters(hosters: list[Hoster]) -> list[Hoster]:
    """Sort hosters by (language priority, hoster priority).

    Hosters whose language is not in the configured priority are dropped.
    """
    lang_pri = config.language_priority()
    host_pri = [h.lower() for h in config.hoster_priority()]

    def lang_rank(h: Hoster) -> int:
        return lang_pri.index(h.lang) if h.lang in lang_pri else len(lang_pri)

    def host_rank(h: Hoster) -> int:
        name = h.name.lower()
        return host_pri.index(name) if name in host_pri else len(host_pri)

    candidates = [h for h in hosters if h.lang in lang_pri]
    return sorted(candidates, key=lambda h: (lang_rank(h), host_rank(h)))


def resolve_stream(
    hosters: list[Hoster],
    report: Optional[Callable[[str], None]] = None,
) -> tuple[Stream | None, Hoster | None]:
    """Try ordered hosters until one extractor yields a Stream.

    ``report`` receives German status lines (defaults to no-op). Returns the
    resolved ``(Stream, Hoster)`` or ``(None, None)`` if all candidates fail.
    """
    say = report or (lambda _msg: None)
    session = http.get_session()
    for hoster in order_hosters(hosters):
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
