# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Based on ani-cli by pystardust: https://github.com/pystardust/ani-cli

"""Entry point and argparse wiring."""

from __future__ import annotations

import argparse
import sys

from . import __version__, i18n


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aniworld-cli",
        description="aniworld.to – Streaming-CLI (mpv).",
    )
    p.add_argument("query", nargs="?", help="Suchbegriff (optional)")
    p.add_argument("--lang", help="Sprachpriorität, z. B. ger-dub,ger-sub,eng-sub")
    p.add_argument("--hoster", help="Hoster-Priorität, kommagetrennt")
    p.add_argument(
        "--episode",
        metavar="S-E",
        help="Direkt Staffel-Folge wählen, z. B. 1-3 (oder 0-1 für Filme)",
    )
    p.add_argument(
        "--no-menu",
        action="store_true",
        help="Nur Argumente verwenden, keine interaktiven Menüs",
    )
    p.add_argument(
        "--auto",
        action="store_true",
        help="Auto-Modus: nach jeder Folge automatisch die nächste starten",
    )
    p.add_argument(
        "--watchlist",
        "-w",
        action="store_true",
        help="Aus zuletzt gesehenen Serien wählen, ohne zu suchen",
    )
    p.add_argument("--player", help="Pfad zu mpv (sonst aus PATH)")
    p.add_argument(
        "--debug",
        action="store_true",
        help="Stream-URL + Header auflösen und ausgeben, mpv nicht starten",
    )
    p.add_argument("--version", action="version", version=f"aniworld-cli {__version__}")
    return p


def _apply_env_overrides(args: argparse.Namespace) -> None:
    """Let --lang / --hoster feed config via env, the documented override path."""
    import os

    if args.lang:
        os.environ["ANIWORLD_LANG"] = args.lang
    if args.hoster:
        os.environ["ANIWORLD_HOSTER"] = args.hoster


def _force_utf8_stdio() -> None:
    """Avoid mojibake for German text on legacy Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdio()
    args = build_parser().parse_args(argv)
    _apply_env_overrides(args)

    # Import after env overrides so config picks them up.
    import requests

    from . import cli
    from .http import CloudflareChallenge

    try:
        return cli.run(args)
    except KeyboardInterrupt:
        print()
        print(i18n.t("goodbye"))
        return 130
    except CloudflareChallenge:
        print(i18n.t("cloudflare_block"))
        return 1
    except requests.RequestException:
        if args.debug:
            raise
        print(i18n.t("network_error"))
        return 1
    except Exception:  # noqa: BLE001 - never show a raw traceback to the user
        if args.debug:
            raise
        print(i18n.t("unexpected_error"))
        return 1


if __name__ == "__main__":
    sys.exit(main())
