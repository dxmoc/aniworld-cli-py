"""mpv detection and launch via subprocess (no shell, cross-platform)."""

from __future__ import annotations

import shutil
import subprocess
import sys

from . import i18n
from .models import Stream


class PlayerNotFound(Exception):
    """Raised when no usable mpv binary can be located."""


def find_mpv(explicit: str | None = None) -> str | None:
    """Return a path to mpv, or None. ``explicit`` (from --player) wins."""
    if explicit:
        # Accept an absolute/relative path or a name resolvable on PATH.
        return shutil.which(explicit) or (explicit if _looks_executable(explicit) else None)
    return shutil.which("mpv")


def _looks_executable(path: str) -> bool:
    import os

    return os.path.isfile(path) and os.access(path, os.X_OK)


def install_hint() -> str:
    """OS-appropriate install hint for mpv."""
    if sys.platform.startswith("win"):
        return i18n.t("mpv_hint_windows")
    return i18n.t("mpv_hint_linux")


def build_command(mpv_path: str, stream: Stream, title: str | None = None) -> list[str]:
    """Build the mpv argv from the resolved stream and its required headers.

    User-Agent is passed via mpv's dedicated ``--user-agent`` flag rather than
    folded into ``--http-header-fields``: ffmpeg always emits a User-Agent of its
    own, so adding a second one through the header-fields list produces a
    duplicate header that some CDNs reject with HTTP 400. Remaining headers
    (e.g. Referer) go into ``--http-header-fields``.

    ``title`` (e.g. "Naruto – S03E12") is passed via ``--force-media-title`` so
    mpv shows the episode name instead of the opaque, tokenised CDN URL.
    """
    cmd = [mpv_path]
    headers = dict(stream.headers)
    user_agent = next(
        (headers.pop(k) for k in list(headers) if k.lower() == "user-agent"), None
    )
    if user_agent:
        cmd.append(f"--user-agent={user_agent}")
    if headers:
        fields = ",".join(f"{k}: {v}" for k, v in headers.items())
        cmd.append(f"--http-header-fields={fields}")
    if title:
        cmd.append(f"--force-media-title={title}")
    cmd.append(stream.url)
    return cmd


def play(stream: Stream, mpv_path: str | None = None, title: str | None = None) -> int:
    """Launch mpv for ``stream``. Returns mpv's exit code.

    Raises PlayerNotFound if mpv is unavailable.
    """
    resolved = find_mpv(mpv_path)
    if not resolved:
        raise PlayerNotFound(install_hint())
    cmd = build_command(resolved, stream, title)
    proc = subprocess.run(cmd)  # noqa: S603 - argv list, no shell
    return proc.returncode
