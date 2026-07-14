"""Persistent watch state: resume points and an implicit watchlist.

A single JSON file records, per series slug, the last episode you played plus the
series' title/url and a timestamp. That one structure powers both "continue
watching" (resume) and the watchlist (every series you have watched). Everything
degrades gracefully: a missing or corrupt file is treated as empty, and writes
never raise into the playback flow.

Location (override with ``ANIWORLD_STATE_DIR``):
* Windows: ``%APPDATA%\\aniworld-cli\\state.json``
* Linux/macOS: ``$XDG_CONFIG_HOME/aniworld-cli/state.json`` (``~/.config/...``)
"""

from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

from .models import Episode, Series

STATE_VERSION = 1


def _state_dir() -> Path:
    override = os.environ.get("ANIWORLD_STATE_DIR")
    if override:
        return Path(override)
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return Path(base) / "aniworld-cli"
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return Path(base) / "aniworld-cli"


def _state_file() -> Path:
    return _state_dir() / "state.json"


def load() -> dict:
    """Return the parsed state, or an empty skeleton if absent/unreadable."""
    try:
        with _state_file().open(encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {"version": STATE_VERSION, "series": {}}
    if not isinstance(data, dict) or not isinstance(data.get("series"), dict):
        return {"version": STATE_VERSION, "series": {}}
    return data


def save(data: dict) -> None:
    """Write state atomically-ish; never raise into the caller."""
    try:
        directory = _state_dir()
        directory.mkdir(parents=True, exist_ok=True)
        tmp = _state_file().with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        tmp.replace(_state_file())
    except OSError:
        pass


def _now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def record(series: Series, episode: Episode) -> None:
    """Remember ``episode`` as the resume point for ``series``."""
    data = load()
    data.setdefault("series", {})[series.slug] = {
        "title": series.title,
        "url": series.url,
        "season": episode.season,
        "number": episode.number,
        "label": episode.label,
        "updated": _now(),
    }
    save(data)


def get_progress(slug: str) -> dict | None:
    """Return the stored resume entry for ``slug``, or None."""
    entry = load().get("series", {}).get(slug)
    return entry if isinstance(entry, dict) else None


def list_entries() -> list[dict]:
    """All watched series as raw entries, most recently watched first."""
    series = load().get("series", {})
    entries = [{"slug": slug, **info} for slug, info in series.items() if isinstance(info, dict)]
    entries.sort(key=lambda e: e.get("updated", ""), reverse=True)
    return entries


def list_series() -> list[Series]:
    """Watched series as :class:`Series` objects, most recent first."""
    return [
        Series(title=e.get("title", e["slug"]), slug=e["slug"], url=e.get("url", ""))
        for e in list_entries()
    ]


def remove(slug: str) -> None:
    """Drop a series from the state (e.g. finished/unwanted)."""
    data = load()
    if data.get("series", {}).pop(slug, None) is not None:
        save(data)
