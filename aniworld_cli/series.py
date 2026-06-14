"""Series -> seasons/episodes.

Verified against the live site. The series/season pages carry a navigation block
``<div id="stream" class="hosterSiteDirectNav">`` with:

* a season ``<ul>`` of links ``/anime/stream/<slug>/staffel-<n>`` plus an optional
  ``/anime/stream/<slug>/filme`` entry (films), and
* an episode ``<ul>`` listing only the *currently active* season's episodes.

So to enumerate a season we fetch that season's own page and read its episode
list. Films use ``/filme/film-<n>``; we model the films section as season 0.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from . import config, http
from .models import Episode, Series

FILMS_SEASON = 0


def _soup(markup: str) -> BeautifulSoup:
    return BeautifulSoup(markup, "html.parser")


def _nav(soup: BeautifulSoup):
    return soup.select_one("div#stream")


def season_path(slug: str, season: int) -> str:
    if season == FILMS_SEASON:
        return f"/anime/stream/{slug}/filme"
    return f"/anime/stream/{slug}/staffel-{season}"


def parse_seasons(markup: str, slug: str) -> list[int]:
    """Season numbers from the nav block; 0 == films. Sorted, deduped."""
    soup = _soup(markup)
    nav = _nav(soup)
    found: set[int] = set()
    scope = nav.find_all("a", href=True) if nav else []
    staffel = re.compile(rf"^/anime/stream/{re.escape(slug)}/staffel-(\d+)/?$")
    filme = re.compile(rf"^/anime/stream/{re.escape(slug)}/filme/?$")
    for a in scope:
        href = a["href"]
        m = staffel.match(href)
        if m:
            found.add(int(m.group(1)))
        elif filme.match(href):
            found.add(FILMS_SEASON)
    return sorted(found)


def parse_episodes(markup: str, slug: str, season: int) -> list[Episode]:
    """Episodes for ``season`` from that season page's nav block. Deduped."""
    soup = _soup(markup)
    nav = _nav(soup)
    if season == FILMS_SEASON:
        pat = re.compile(rf"^/anime/stream/{re.escape(slug)}/filme/film-(\d+)/?$")
    else:
        pat = re.compile(
            rf"^/anime/stream/{re.escape(slug)}/staffel-{season}/episode-(\d+)/?$"
        )
    seen: set[int] = set()
    episodes: list[Episode] = []
    scope = nav.find_all("a", href=True) if nav else []
    for a in scope:
        m = pat.match(a["href"])
        if not m:
            continue
        number = int(m.group(1))
        if number in seen:
            continue
        seen.add(number)
        episodes.append(
            Episode(
                series_slug=slug,
                url=config.BASE_URL + a["href"],
                season=season,
                number=number,
            )
        )
    episodes.sort(key=lambda e: e.number)
    return episodes


def list_seasons(series: Series) -> list[int]:
    """Fetch the series page and return its season numbers (0 == films)."""
    resp = http.get(series.url)
    return parse_seasons(resp.text, series.slug)


def list_episodes(series: Series, season: int) -> list[Episode]:
    """Fetch a season page and return its episodes."""
    url = config.BASE_URL + season_path(series.slug, season)
    resp = http.get(url)
    return parse_episodes(resp.text, series.slug, season)
