# Changelog

Notable changes in this fork. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This fork tracks [0liverFlow/CVE2PoC](https://github.com/0liverFlow/CVE2PoC) upstream (v1.0.0); the entries below are what it adds on top.

## [Unreleased]

### Added

- Rosé Pine theming across the CLI: an animated `CVE2POC` startup banner (a light sweeps across the wordmark), palette-coloured results, braille spinners, and an iris progress bar (`core/theme.py`, `core/banner.py`).
- HTML report restyled in Rosé Pine, shipping the Main, Moon, and Dawn palettes with an in-page switcher; the default follows the viewer's OS light/dark setting.
- `CVE2POC_THEME=rose-pine|rose-pine-moon|rose-pine-dawn` to pin a palette. With nothing set, the tool follows the Omarchy current-theme link.
- `--no-anim` (and `CVE2POC_NO_ANIM`) for a static banner; the banner still falls back to static when piped or under `NO_COLOR`.
- A shared, pooled HTTP session with a request timeout and retry/backoff on 429/5xx and connection resets (`core/http.py`).
- An on-disk cache for the CISA KEV, EPSS, ExploitDB, Metasploit, and Nuclei feeds under `~/.cache/cve2poc`, reused for 24 hours (`core/cache.py`). Flags: `--refresh`, `--no-cache`, `--clear-cache`. An offline run falls back to a stale cache instead of failing.
- A network-free pytest suite in `tests/` and a GitHub Actions workflow running ruff and pytest.
- SVG and animated GIF banners in `assets/`.

### Changed

- API keys moved out of the installed package (`core/.env`) to `~/.config/cve2poc/.env` (XDG), so `pipx`/`uv` upgrades no longer wipe them. An existing in-package `.env` is migrated on first run.
- All 37 network calls now go through the shared session; previously each was a bare `requests.get` with no timeout.
- Exit codes are consistent: `0` success, `2` usage or config error, `3` network unreachable, `130` interrupted. `main()` wraps the run so the codes apply to the installed `cve2poc` command, not only `python -m`.
- Project URLs point at the DAEMON-404 fork; upstream credit is kept in the README and the banner.

### Fixed

- A slow or unreachable host no longer hangs the whole run.
- `sys.exit(-1)`, which surfaced as exit code 255, is now `sys.exit(2)`.
- Removed dead imports in `mitigations.py`.

## Credits

Upstream tool by [0liverFlow](https://github.com/0liverFlow/CVE2PoC), GPLv3. This fork re-skins it in Rosé Pine and hardens the networking; it changes no detection logic.
