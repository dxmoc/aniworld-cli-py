"""Search: query -> list[Series]. Implemented in M2 against the live site."""

from __future__ import annotations

from .models import Series


def search(query: str) -> list[Series]:
    """Return series matching ``query``. (M2)"""
    raise NotImplementedError("search() wird in M2 umgesetzt")
