# aniworld-cli

Eine schlanke, reine **Streaming-CLI** für [aniworld.to](https://aniworld.to),
inspiriert von `ani-cli`, aber komplett eigenständig in Python geschrieben.
Deutschsprachige Oberfläche, läuft unter Linux und Windows (PowerShell oder WSL).
Wiedergabe ausschließlich über **mpv** – kein Download.

## Funktionen

- Suche über die AJAX-Schnittstelle von aniworld.to
- Auswahl von Serie → Staffel (inkl. Filme) → Folge per Pfeiltasten (`questionary`)
- Sprachpriorität **German Dub → German Sub → Eng Sub** (konfigurierbar)
- Hoster-Fallback nach Priorität; aktuell verifizierte Extraktoren:
  **VOE**, **Doodstream**, **Vidmoly**. **Filemoon** ist „best effort“
  (die Seite liefert dort inzwischen eine JS-App; gelingt die Auflösung nicht,
  wird automatisch der nächste Hoster versucht).
- „Nächste Folge / Andere Folge / Beenden“-Schleife nach der Wiedergabe
- `--debug` löst die finale Stream-URL auf und gibt sie aus, ohne mpv zu starten

## Voraussetzungen

- Python **3.9+**
- [mpv](https://mpv.io/) im `PATH` (oder via `--player <pfad>`)
  - Linux: `sudo pacman -S mpv` / `sudo apt install mpv` / `sudo dnf install mpv`
  - Windows: `scoop install mpv` oder `winget install mpv`

## Installation

```bash
python -m venv .venv
# Linux:        source .venv/bin/activate
# Windows (PS): .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# optional, als Befehl "aniworld-cli":
pip install -e .
```

## Verwendung

```bash
# Interaktiv (fragt nach dem Suchbegriff):
python -m aniworld_cli

# Mit Suchbegriff:
python -m aniworld_cli "naruto"

# Direkt eine bestimmte Folge ohne Menüs (Staffel-Folge, 0-N = Filme):
python -m aniworld_cli "naruto" --no-menu --episode 1-1

# Nur die finale URL + Header auflösen (kein mpv):
python -m aniworld_cli "naruto" --episode 1-1 --debug
```

### Argumente

| Argument          | Bedeutung                                                       |
|-------------------|-----------------------------------------------------------------|
| `query`           | Suchbegriff (optional; sonst wird gefragt)                      |
| `--lang`          | Sprachpriorität, z. B. `ger-dub,ger-sub,eng-sub`                |
| `--hoster`        | Hoster-Priorität, kommagetrennt                                 |
| `--episode S-E`   | Direkt Staffel-Folge wählen, z. B. `1-3` (oder `0-1` für Filme) |
| `--no-menu`       | Nur Argumente verwenden, keine interaktiven Menüs               |
| `--player <pfad>` | Pfad zu mpv (sonst aus `PATH`)                                  |
| `--debug`         | Stream-URL + Header ausgeben, mpv nicht starten                 |

Sprach- und Hoster-Priorität lassen sich auch per Umgebungsvariablen setzen:
`ANIWORLD_LANG`, `ANIWORLD_HOSTER`, `ANIWORLD_BASE_URL`, `ANIWORLD_UA`.

## Tests

Die Parser werden offline gegen gespeicherte HTML-/JSON-Beispiele in
`tests/fixtures/` geprüft (kein Netzwerk in den Tests):

```bash
pip install pytest
python -m pytest -q
```

Manueller Smoke-Test mit echtem Netzwerk:

```bash
python -m aniworld_cli "naruto" --episode 1-1 --debug
```

## Hinweise

- aniworld.to sitzt hinter einem Anti-Bot-Schutz. Bei einer Cloudflare-Sperre
  meldet die CLI dies klar; als *optionaler externer* Helfer kann
  [`flaresolverr`](https://github.com/FlareSolverr/FlareSolverr) dienen
  (nicht enthalten).
- Hoster und Seitenstruktur ändern sich. Extraktoren werden gegen die *Live*-Seite
  verifiziert; bei Bedarf neue Fixtures speichern und Parser anpassen.

## Rechtlicher Hinweis

Dies ist ein reines Client-Werkzeug für den Zugriff und hostet selbst keine
Inhalte. Für eine rechtmäßige Nutzung ist allein der Nutzer verantwortlich.
