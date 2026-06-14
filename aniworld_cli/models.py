"""Plain data containers used across the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Series:
    """A search result / series landing page."""

    title: str
    slug: str
    url: str
    description: str = ""

    @property
    def display(self) -> str:
        return self.title


@dataclass(frozen=True)
class Episode:
    """A single playable episode (or movie)."""

    series_slug: str
    url: str
    season: int  # 0 == movies/films section
    number: int
    title: str = ""

    @property
    def label(self) -> str:
        if self.season == 0:
            return f"Film {self.number}" + (f" – {self.title}" if self.title else "")
        return (
            f"S{self.season:02d}E{self.number:02d}"
            + (f" – {self.title}" if self.title else "")
        )


@dataclass(frozen=True)
class Hoster:
    """A hoster entry on an episode page.

    ``lang_key`` is the site's raw integer language marker. ``lang`` is our
    canonical token (see config), resolved via the page's language switch UI.
    ``redirect_url`` leads to the hoster's embed page.
    """

    name: str
    lang_key: int
    lang: str
    redirect_url: str


@dataclass(frozen=True)
class Stream:
    """The final resolved stream handed to the player."""

    url: str
    headers: dict[str, str] = field(default_factory=dict)
