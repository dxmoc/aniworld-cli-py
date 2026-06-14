"""Episode -> list[Hoster] with language markers. Implemented in M3."""

from __future__ import annotations

from .models import Episode, Hoster


def list_hosters(episode: Episode) -> list[Hoster]:
    """Return hoster entries for an episode, with resolved languages. (M3)"""
    raise NotImplementedError("list_hosters() wird in M3 umgesetzt")
