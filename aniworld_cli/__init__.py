"""aniworld-cli: streaming-only CLI for aniworld.to."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("aniworld-cli")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"
