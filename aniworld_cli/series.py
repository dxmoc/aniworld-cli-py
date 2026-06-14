"""Series -> seasons/episodes. Implemented in M3 against the live site."""

from __future__ import annotations

from .models import Episode, Series


def list_seasons(series: Series) -> list[int]:
    """Return available season numbers (0 == movies). (M3)"""
    raise NotImplementedError("list_seasons() wird in M3 umgesetzt")


def list_episodes(series: Series, season: int) -> list[Episode]:
    """Return episodes for a season. (M3)"""
    raise NotImplementedError("list_episodes() wird in M3 umgesetzt")
