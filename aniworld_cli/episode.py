"""Episode -> list[Hoster] with resolved languages.

Verified against the live site. The episode page contains:

* a language switch ``<div class="changeLanguageBox">`` with ``<img>`` flags
  carrying ``data-lang-key`` (an integer). The mapping from that integer to a
  human language is read off the flag image/alt/title here — never hardcoded.
* a hoster ``<ul class="row">`` whose ``<li>`` items each carry ``data-lang-key``,
  ``data-link-target="/redirect/<id>"`` and an ``<h4>`` hoster name.
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from . import config, http
from .models import Episode, Hoster


def _soup(markup: str) -> BeautifulSoup:
    return BeautifulSoup(markup, "html.parser")


def _classify_language(*texts: str) -> str:
    """Map a flag's image/alt/title text to one of our canonical tokens.

    Order matters: the subtitle variants also contain the word "german"/"deutsch"
    (e.g. ``japanese-german.svg`` / "mit Untertitel Deutsch"), so they must be
    tested before the plain dub case.
    """
    blob = " ".join(t for t in texts if t).lower()
    if "japanese-german" in blob or "untertitel deutsch" in blob or "ger-sub" in blob:
        return config.LANG_GER_SUB
    if (
        "japanese-english" in blob
        or "untertitel englisch" in blob
        or "english" in blob
        or "englisch" in blob
    ):
        return config.LANG_ENG_SUB
    if "german" in blob or "deutsch" in blob:
        return config.LANG_GER_DUB
    return ""


def parse_language_map(markup: str) -> dict[int, str]:
    """Discover the page's lang-key -> canonical-token mapping."""
    soup = _soup(markup)
    box = soup.select_one(".changeLanguageBox")
    mapping: dict[int, str] = {}
    if not box:
        return mapping
    for img in box.find_all("img", attrs={"data-lang-key": True}):
        try:
            key = int(img["data-lang-key"])
        except (TypeError, ValueError):
            continue
        token = _classify_language(
            img.get("src", ""), img.get("alt", ""), img.get("title", "")
        )
        mapping[key] = token or f"lang-{key}"
    return mapping


def parse_hosters(markup: str, lang_map: dict[int, str] | None = None) -> list[Hoster]:
    """Parse the hoster list, attaching the resolved language to each entry."""
    soup = _soup(markup)
    if lang_map is None:
        lang_map = parse_language_map(markup)
    hosters: list[Hoster] = []
    for li in soup.select("li[data-link-target][data-lang-key]"):
        target = li.get("data-link-target", "")
        if not target.startswith("/redirect/"):
            continue
        try:
            key = int(li["data-lang-key"])
        except (TypeError, ValueError):
            continue
        h4 = li.find("h4")
        name = h4.get_text(strip=True) if h4 else ""
        if not name:
            continue
        hosters.append(
            Hoster(
                name=name,
                lang_key=key,
                lang=lang_map.get(key, f"lang-{key}"),
                redirect_url=config.BASE_URL + target,
            )
        )
    return hosters


def list_hosters(episode: Episode) -> list[Hoster]:
    """Fetch the episode page and return its hoster entries with languages."""
    resp = http.get(episode.url)
    return parse_hosters(resp.text)
