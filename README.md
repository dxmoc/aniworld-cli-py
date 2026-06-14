# aniworld-cli

> Eine schlanke, reine **Streaming-CLI** für [aniworld.to](https://aniworld.to) –
> komplett eigenständig in Python geschrieben, mit deutscher Oberfläche.
> Wiedergabe ausschließlich über **mpv**. Kein Download.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-green)](LICENSE)
[![Platforms](https://img.shields.io/badge/os-Linux%20%7C%20Windows%20%7C%20WSL-lightgrey)]()

---

## Inhalt

- [Funktionen](#funktionen)
- [Schnellstart](#schnellstart)
- [1 · mpv installieren](#1--mpv-installieren)
- [2 · Projekt einrichten](#2--projekt-einrichten)
- [3 · Tests ausführen](#3--tests-ausführen)
- [4 · Benutzen](#4--benutzen)
- [Argumente & Umgebungsvariablen](#argumente--umgebungsvariablen)
- [Fehlerbehebung](#fehlerbehebung)
- [Rechtliches](#rechtliches)

---

## Funktionen

- 🔍 Suche über die AJAX-Schnittstelle von aniworld.to
- 📺 Auswahl von **Serie → Staffel (inkl. Filme) → Folge** per Pfeiltasten
- 🌐 **Sprachauswahl pro Folge**: bietet eine Folge mehrere Sprachen an
  (z. B. German Dub / German Sub / Eng Sub), erscheint ein Menü; die Wahl wird
  für die nächsten Folgen gemerkt. Mit `--lang` oder `--no-menu` greift
  stattdessen automatisch die Prioritätsreihenfolge.
- 🔁 Hoster-Fallback nach Priorität – verifizierte Extraktoren: **VOE**,
  **Doodstream**, **Vidmoly** (Filemoon „best effort")
- ⏭️ „Nächste Folge / Andere Folge / Beenden"-Schleife nach der Wiedergabe
- 🐞 `--debug` löst die finale Stream-URL auf, ohne mpv zu starten

---

## Schnellstart

```bash
# 1. mpv installieren (siehe unten je nach Betriebssystem)
# 2. Repo holen
git clone https://github.com/dxmoc/aniworld-cli-py.git
cd aniworld-cli-py

# 3. Virtuelle Umgebung + Abhängigkeiten
python -m venv .venv
# Linux/macOS/WSL:
source .venv/bin/activate
# Windows PowerShell:
#   .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 4. Starten
python -m aniworld_cli "naruto"
```

---

## 1 · mpv installieren

aniworld-cli spielt ausschließlich über **[mpv](https://mpv.io/)** ab. mpv muss
im `PATH` liegen (oder per `--player <pfad>` übergeben werden).

### 🐧 Linux

| Distribution      | Befehl                          |
|-------------------|---------------------------------|
| Arch / Manjaro    | `sudo pacman -S mpv`            |
| Debian / Ubuntu   | `sudo apt install mpv`          |
| Fedora            | `sudo dnf install mpv`          |

### 🪟 Windows (PowerShell)

```powershell
winget install --id shinchiro.mpv
# oder:
scoop install mpv
```

> Nach der Installation ggf. ein **neues** Terminal öffnen, damit der `PATH`
> aktualisiert ist. Test: `mpv --version`.

### 🐧🪟 WSL (Ubuntu unter Windows)

```bash
sudo apt update && sudo apt install mpv
```

> In WSL ohne GUI-Setup öffnet mpv kein Fenster. Nutze `--debug` zum Auflösen
> der URL, oder ein WSLg-fähiges Windows 11 für echte Wiedergabe.

**Prüfen:**

```bash
mpv --version
```

---

## 2 · Projekt einrichten

Voraussetzung: **Python 3.9+** und **git**.

<details>
<summary>🐧 <b>Linux / macOS / WSL</b></summary>

```bash
git clone https://github.com/dxmoc/aniworld-cli-py.git
cd aniworld-cli-py

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```
</details>

<details open>
<summary>🪟 <b>Windows PowerShell</b></summary>

```powershell
git clone https://github.com/dxmoc/aniworld-cli-py.git
cd aniworld-cli-py

py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

> Falls das Aktivieren mit „Ausführung von Skripten ist deaktiviert" scheitert:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```
> (gilt nur für die aktuelle Sitzung).
</details>

Optional als systemweiter Befehl `aniworld-cli`:

```bash
pip install -e .
```

---

## 3 · Tests ausführen

Die Parser werden **offline** gegen gespeicherte HTML-/JSON-Beispiele in
`tests/fixtures/` geprüft – kein Netzwerk nötig, schnell und deterministisch.

```bash
pip install pytest
python -m pytest -q
```

Erwartete Ausgabe: alle Tests grün (`… passed`).

**Manueller Smoke-Test mit echtem Netzwerk** (löst die finale Stream-URL auf,
ohne mpv zu starten):

```bash
python -m aniworld_cli "naruto" --episode 1-1 --debug
```

Gibt eine `…/master.m3u8`-URL plus Header aus, wenn alles funktioniert.

---

## 4 · Benutzen

```bash
# Interaktiv (fragt nach dem Suchbegriff):
python -m aniworld_cli

# Mit Suchbegriff – führt durch Serie/Staffel/Folge:
python -m aniworld_cli "naruto"

# Direkt eine bestimmte Folge ohne Menüs (Staffel-Folge; 0-N = Filme):
python -m aniworld_cli "naruto" --no-menu --episode 1-1

# Englische Untertitel bevorzugen:
python -m aniworld_cli "one piece" --lang eng-sub

# Eigener mpv-Pfad (falls nicht im PATH):
python -m aniworld_cli "naruto" --player "C:\Program Files\MPV Player\mpv.exe"
```

Nach der Wiedergabe erscheint das Menü **Nächste Folge / Andere Folge / Beenden**.

---

## Argumente & Umgebungsvariablen

| Argument          | Bedeutung                                                       |
|-------------------|-----------------------------------------------------------------|
| `query`           | Suchbegriff (optional; sonst wird gefragt)                      |
| `--lang`          | Sprachpriorität, z. B. `ger-dub,ger-sub,eng-sub`                |
| `--hoster`        | Hoster-Priorität, kommagetrennt                                 |
| `--episode S-E`   | Direkt Staffel-Folge wählen, z. B. `1-3` (oder `0-1` für Filme) |
| `--no-menu`       | Nur Argumente verwenden, keine interaktiven Menüs               |
| `--player <pfad>` | Pfad zu mpv (sonst aus `PATH`)                                  |
| `--debug`         | Stream-URL + Header ausgeben, mpv nicht starten                 |
| `--version`       | Version anzeigen                                                |

Gleiche Einstellungen per Umgebungsvariable:

| Variable           | Wirkung                                  |
|--------------------|------------------------------------------|
| `ANIWORLD_LANG`    | Sprachpriorität (wie `--lang`)           |
| `ANIWORLD_HOSTER`  | Hoster-Priorität (wie `--hoster`)        |
| `ANIWORLD_BASE_URL`| Abweichende Basis-URL                    |
| `ANIWORLD_UA`      | Eigener User-Agent                       |

---

## Fehlerbehebung

| Symptom | Ursache / Lösung |
|---------|------------------|
| `mpv wurde nicht gefunden` | mpv installieren (siehe [Schritt 1](#1--mpv-installieren)) oder `--player <pfad>` nutzen. |
| Cloudflare-/Anti-Bot-Meldung | Die Seite blockt Bots. Optional hilft ein **externer** [`flaresolverr`](https://github.com/FlareSolverr/FlareSolverr)-Dienst (nicht enthalten). |
| `Kein Hoster lieferte einen abspielbaren Stream` | Hoster gerade nicht verfügbar; später erneut versuchen oder anderen Titel/Folge wählen. |
| Umlaute kaputt in der Konsole | Wird automatisch auf UTF-8 gesetzt; bei alten Windows-Konsolen hilft `chcp 65001`. |
| Wiedergabe startet nicht in WSL | Kein GUI-Backend – `--debug` nutzen oder WSLg (Windows 11). |

Mehr Details zu Fehlern liefert das `--debug`-Flag (zeigt dann auch vollständige
Tracebacks statt einer freundlichen deutschen Meldung).

---

## Hinweise für Entwickler

- aniworld.to ändert Markup und Hoster regelmäßig. Extraktoren werden gegen die
  **Live**-Seite verifiziert; neue Beispiele bei Bedarf in `tests/fixtures/`
  ablegen und Parser anpassen.
- Architektur: `search.py` → `series.py`/`episode.py` → `resolve.py` →
  `extractors/<hoster>.py` → `player.py`. Alle deutschen Texte liegen in
  `i18n.py`.

---

## Rechtliches

Lizenz: **GNU GPL v3.0 oder später** – siehe [LICENSE](LICENSE).
Copyright © 2026 dxmoc.

Dies ist ein reines **Client-Werkzeug** für den Zugriff und hostet selbst keine
Inhalte. Für eine rechtmäßige Nutzung ist allein der Nutzer verantwortlich.
