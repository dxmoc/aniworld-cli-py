# aniworld-cli

> A lean, **streaming-only CLI** for [aniworld.to](https://aniworld.to) –
> written from scratch in pure Python, with a German user interface.
> Playback runs exclusively through **mpv**. No downloads.

[![tests](https://github.com/dxmoc/aniworld-cli-py/actions/workflows/tests.yml/badge.svg)](https://github.com/dxmoc/aniworld-cli-py/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platforms](https://img.shields.io/badge/os-Linux%20%7C%20Windows%20%7C%20WSL-lightgrey)]()

> **Note:** The on-screen text of the app is **German** (it targets aniworld.to,
> a German anime site). This README is in English; the CLI prompts are not.

---

## Contents

- [Features](#features)
- [Quick start](#quick-start)
- [1 · Install mpv](#1--install-mpv)
- [2 · Set up the project](#2--set-up-the-project)
- [3 · Run the tests](#3--run-the-tests)
- [4 · Usage](#4--usage)
- [Arguments & environment variables](#arguments--environment-variables)
- [Troubleshooting](#troubleshooting)
- [Legal](#legal)

---

## Features

- Search via aniworld.to's AJAX endpoint
- Pick **series → season (incl. movies) → episode** with arrow keys
- **Per-episode language/subtitle selection**: when an episode offers more
  than one language (e.g. German Dub / German Sub / Eng Sub) a menu appears, and
  your choice is remembered for the next episodes. With `--lang` or `--no-menu`
  the configured priority order is used automatically instead.
- Hoster fallback by priority – currently verified working: **VOE** and
  **Vidmoly** (see [hoster status](#hoster-status) for the rest)
- "Next episode / Other episode / Quit" loop after playback
- `--debug` resolves the final stream URL without launching mpv

---

## Quick start

```bash
# 1. Install mpv (see per-OS instructions below)
# 2. Get the repo
git clone https://github.com/dxmoc/aniworld-cli-py.git
cd aniworld-cli-py

# 3. Virtual environment + dependencies
python -m venv .venv
# Linux/macOS/WSL:
source .venv/bin/activate
# Windows PowerShell:
#   .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 4. Run
python -m aniworld_cli "naruto"
```

---

## 1 · Install mpv

aniworld-cli plays exclusively through **[mpv](https://mpv.io/)**. mpv must be on
your `PATH` (or passed via `--player <path>`).

### Linux

| Distribution      | Command                          |
|-------------------|----------------------------------|
| Arch / Manjaro    | `sudo pacman -S mpv`            |
| Debian / Ubuntu   | `sudo apt install mpv`          |
| Fedora            | `sudo dnf install mpv`          |

### Windows (PowerShell)

```powershell
winget install --id shinchiro.mpv
# or:
scoop install mpv
```

> The `shinchiro.mpv` package does **not** add mpv to your `PATH` automatically.
> Either add its folder (e.g. `C:\Program Files\MPV Player`) to your user `PATH`,
> open a **new** terminal, or pass `--player "C:\Program Files\MPV Player\mpv.exe"`.
> Verify with `mpv --version`.

### WSL (Ubuntu on Windows)

```bash
sudo apt update && sudo apt install mpv
```

> Without a GUI setup, mpv won't open a window in WSL. Use `--debug` to just
> resolve the URL, or a WSLg-capable Windows 11 for real playback.

**Check:**

```bash
mpv --version
```

---

## 2 · Set up the project

Requires **Python 3.9+** and **git**.

<details>
<summary><b>Linux / macOS / WSL</b></summary>

```bash
git clone https://github.com/dxmoc/aniworld-cli-py.git
cd aniworld-cli-py

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```
</details>

<details open>
<summary><b>Windows PowerShell</b></summary>

```powershell
git clone https://github.com/dxmoc/aniworld-cli-py.git
cd aniworld-cli-py

py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

> If activation fails with "running scripts is disabled on this system":
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```
> (applies to the current session only).
</details>

Optional, as a system-wide `aniworld-cli` command:

```bash
pip install -e .
```

---

## 3 · Run the tests

The parsers are tested **offline** against saved HTML/JSON samples in
`tests/fixtures/` – no network needed, fast and deterministic.

```bash
pip install pytest
python -m pytest -q
```

Expected: all tests green (`… passed`).

**Manual smoke test with real network** (resolves the final stream URL without
launching mpv):

```bash
python -m aniworld_cli "naruto" --episode 1-1 --debug
```

Prints a `…/master.m3u8` URL plus headers when everything works.

---

## 4 · Usage

```bash
# Interactive (asks for a search term):
python -m aniworld_cli

# With a search term – guides you through series/season/episode:
python -m aniworld_cli "naruto"

# Jump straight to one episode without menus (season-episode; 0-N = movies):
python -m aniworld_cli "naruto" --no-menu --episode 1-1

# Prefer English subtitles:
python -m aniworld_cli "one piece" --lang eng-sub

# Custom mpv path (if not on PATH):
python -m aniworld_cli "naruto" --player "C:\Program Files\MPV Player\mpv.exe"
```

After playback you get a **Next episode / Other episode / Quit** menu.

---

## Arguments & environment variables

| Argument          | Meaning                                                          |
|-------------------|------------------------------------------------------------------|
| `query`           | Search term (optional; prompted otherwise)                       |
| `--lang`          | Language priority, e.g. `ger-dub,ger-sub,eng-sub`                |
| `--hoster`        | Hoster priority, comma-separated                                 |
| `--episode S-E`   | Pick a season-episode directly, e.g. `1-3` (or `0-1` for movies) |
| `--no-menu`       | Use arguments only, no interactive menus                         |
| `--player <path>` | Path to mpv (otherwise taken from `PATH`)                        |
| `--debug`         | Print stream URL + headers, do not launch mpv                    |
| `--version`       | Show the version                                                 |

The same settings via environment variables:

| Variable            | Effect                                  |
|---------------------|-----------------------------------------|
| `ANIWORLD_LANG`     | Language priority (like `--lang`)       |
| `ANIWORLD_HOSTER`   | Hoster priority (like `--hoster`)       |
| `ANIWORLD_BASE_URL` | Override the base URL                   |
| `ANIWORLD_UA`       | Custom User-Agent                       |

Language tokens: `ger-dub` (German dub), `ger-sub` (German subtitles),
`eng-sub` (English subtitles).

---

## Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `mpv wurde nicht gefunden` | Install mpv (see [step 1](#1--install-mpv)) or use `--player <path>`. |
| Cloudflare / anti-bot message | The site is blocking bots. An **external** [`flaresolverr`](https://github.com/FlareSolverr/FlareSolverr) service can help (not bundled). |
| `Kein Hoster lieferte einen abspielbaren Stream` | Hosters temporarily unavailable; retry later or pick another title/episode. |
| Garbled umlauts in the console | UTF-8 is forced automatically; on old Windows consoles `chcp 65001` helps. |
| Playback won't start in WSL | No GUI backend – use `--debug`, or WSLg (Windows 11). |

The `--debug` flag also shows full tracebacks instead of a friendly German
message, which helps when reporting issues.

---

## Hoster status

aniworld.to changes hosters and their embed markup regularly, so extractor
health drifts over time. Last checked **2026-07-14**:

| Hoster      | Status                                                                |
|-------------|-----------------------------------------------------------------------|
| VOE         | ✅ working                                                             |
| Vidmoly     | ✅ working                                                             |
| Doodstream  | ❌ removed – embed now behind a Cloudflare Turnstile CAPTCHA           |
| Filemoon    | ❌ removed – no longer resolving without a headless browser           |
| Vidoza      | ❌ removed – no longer offered by the site                            |
| SpeedFiles  | ❌ removed – no longer offered by the site                            |
| Streamtape  | ❌ removed – no longer offered by the site                            |

Only **VOE** and **Vidmoly** ship with a working extractor; in a live survey they
cover every episode tried, so the removed hosters cost no real coverage. Adding
one back is a matter of dropping a new module into `aniworld_cli/extractors/` and
registering it — see the extractor contract in that package's `__init__.py`.

## For developers

- aniworld.to changes its markup and hosters regularly. Extractors are verified
  against the **live** site; when needed, save fresh samples into
  `tests/fixtures/` and adjust the parsers.
- Architecture: `search.py` → `series.py`/`episode.py` → `resolve.py` →
  `extractors/<hoster>.py` → `player.py`. All German strings live in `i18n.py`.

---

## Legal

License: **MIT** – see [LICENSE](LICENSE).
Copyright © 2026 dxmoc.

This is a pure **client-side access tool**; it hosts no content itself. The user
is solely responsible for lawful use.
