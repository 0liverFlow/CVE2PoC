"""Rosé Pine theming for CVE2PoC — one palette from the banner to every report.

The whole tool is painted in `Rosé Pine <https://rosepinetheme.com>`_ so it sits
in the same DΛΣMOΘΠ-SEC desktop as the rest of the toolkit. This module owns:

* the three official palettes (Main / Moon / Dawn),
* variant detection (env override, then the Omarchy current-theme link),
* a single shared :class:`rich.console.Console` whose theme re-skins every bit of
  markup the tool already emits, plus semantic style names to use going forward,
* raw-ANSI helpers the animated banner paints itself with,
* the palettes as plain dicts so the HTML report can ship the same switcher.

Colour is chosen by rich automatically: truecolor when the terminal advertises
it, 256-colour otherwise, and nothing at all when piped or ``NO_COLOR`` is set.
"""

from __future__ import annotations

import os
from pathlib import Path

from rich.console import Console
from rich.theme import Theme

VERSION = "1.0.0"
TAGLINE = "from a CVE ID to every public PoC"

# ── Palettes ────────────────────────────────────────────────────────────────
# Values are the canonical Rosé Pine hexes, matched to the rest of the toolkit.

MAIN = {
    "base": "#191724",
    "surface": "#1f1d2e",
    "overlay": "#26233a",
    "muted": "#6e6a86",
    "subtle": "#908caa",
    "text": "#e0def4",
    "love": "#eb6f92",
    "gold": "#f6c177",
    "rose": "#ebbcba",
    "pine": "#31748f",
    "foam": "#9ccfd8",
    "iris": "#c4a7e7",
    "hl_low": "#21202e",
    "hl_med": "#403d52",
    "hl_high": "#524f67",
}

MOON = {
    "base": "#232136",
    "surface": "#2a273f",
    "overlay": "#393552",
    "muted": "#6e6a86",
    "subtle": "#908caa",
    "text": "#e0def4",
    "love": "#eb6f92",
    "gold": "#f6c177",
    "rose": "#ea9a97",
    "pine": "#3e8fb0",
    "foam": "#9ccfd8",
    "iris": "#c4a7e7",
    "hl_low": "#2a283e",
    "hl_med": "#44415a",
    "hl_high": "#56526e",
}

DAWN = {
    "base": "#faf4ed",
    "surface": "#fffaf3",
    "overlay": "#f2e9e1",
    "muted": "#9893a5",
    "subtle": "#797593",
    "text": "#575279",
    "love": "#b4637a",
    "gold": "#ea9d34",
    "rose": "#d7827e",
    "pine": "#286983",
    "foam": "#56949f",
    "iris": "#907aa9",
    "hl_low": "#f4ede8",
    "hl_med": "#dfdad9",
    "hl_high": "#cecacd",
}

PALETTES = {"main": MAIN, "moon": MOON, "dawn": DAWN}
VARIANT_LABEL = {
    "main": "rose-pine",
    "moon": "rose-pine-moon",
    "dawn": "rose-pine-dawn",
}


def _parse_variant(name: str) -> str | None:
    n = name.strip().lower().replace("_", "-").replace("é", "e")
    if n in ("rose-pine", "rosepine", "main", "rose-pine-main"):
        return "main"
    if n in ("rose-pine-moon", "moon"):
        return "moon"
    if n in ("rose-pine-dawn", "dawn", "light"):
        return "dawn"
    return None


def resolve_variant() -> str:
    """Pick a palette: ``CVE2POC_THEME`` first, then the Omarchy theme, then Main."""
    env = os.environ.get("CVE2POC_THEME")
    if env:
        parsed = _parse_variant(env)
        if parsed:
            return parsed
    home = os.environ.get("HOME")
    if home:
        link = Path(home) / ".config/omarchy/current/theme"
        try:
            target = os.readlink(link)
            name = os.path.basename(target.rstrip("/")).lower()
            if "rose" in name or "rosé" in name:
                if "dawn" in name:
                    return "dawn"
                if "moon" in name:
                    return "moon"
                return "main"
        except OSError:
            pass
    return "main"


VARIANT = resolve_variant()
PALETTE = PALETTES[VARIANT]


# ── rich theme ──────────────────────────────────────────────────────────────
def build_theme(p: dict) -> Theme:
    """A rich theme mapping both semantic names and the tool's legacy colours.

    Existing markup (``[red3]``, ``[gold1]``, ``[spring_green2]`` …) is remapped
    onto the palette so nothing has to be rewritten to be re-skinned, while new
    code can use the semantic names (``found``, ``warn``, ``error`` …).
    """
    styles = {
        # raw palette handles
        "base": p["base"],
        "surface": p["surface"],
        "overlay": p["overlay"],
        "muted": p["muted"],
        "subtle": p["subtle"],
        "text": p["text"],
        "love": p["love"],
        "gold": p["gold"],
        "rose": p["rose"],
        "pine": p["pine"],
        "foam": p["foam"],
        "iris": p["iris"],
        # semantic roles (mirrors percival's painter)
        "found": f"bold {p['foam']}",
        "warn": f"bold {p['gold']}",
        "error": f"bold {p['love']}",
        "info": p["pine"],
        "link": p["iris"],
        "accent": p["rose"],
        "category": p["gold"],
        "heading": f"bold {p['iris']}",
        "dim": p["muted"],
        "rule.line": p["hl_high"],
        # severity ramp: foam → gold → rose → love
        "sev.low": p["foam"],
        "sev.medium": p["gold"],
        "sev.high": p["rose"],
        "sev.critical": f"bold {p['love']}",
        # legacy rich colour names used throughout the codebase
        "red3": f"bold {p['love']}",
        "red1": f"bold {p['love']}",
        "bright_red": p["love"],
        "gold1": p["gold"],
        "bright_yellow": p["gold"],
        "dark_orange": p["gold"],
        "orange_red1": p["rose"],
        "green1": f"bold {p['foam']}",
        "spring_green2": p["foam"],
        "bright_cyan": p["foam"],
        "bright_blue": p["pine"],
        "bright_white": p["text"],
        "magenta3": p["iris"],
        # rich built-ins so tables / progress bars adopt the palette too
        "bar.complete": p["iris"],
        "bar.finished": p["foam"],
        "bar.pulse": p["iris"],
        "bar.back": p["hl_med"],
        "progress.description": p["subtle"],
        "progress.percentage": p["gold"],
        "progress.remaining": p["subtle"],
        "progress.elapsed": p["subtle"],
        "progress.spinner": p["iris"],
        "table.header": f"bold {p['iris']}",
        "table.title": f"bold {p['rose']}",
        "table.caption": p["muted"],
        "repr.number": p["gold"],
        "repr.str": p["foam"],
        "repr.url": p["iris"],
    }
    return Theme(styles, inherit=True)


console = Console(theme=build_theme(PALETTE))


def section(title: str) -> None:
    """A percival-style section header: ``❀ Title`` over a thin palette rule."""
    console.print()
    console.print(f"[accent]❀[/accent] [heading]{title}[/heading]")
    console.print(f"[rule.line]{'─' * (len(title) + 2)}[/rule.line]")


def poc_header(title: str) -> str:
    """Markup for a single PoC card header (``▶ PoC n°1``)."""
    return f"\n[heading]▶[/heading] [accent]{title}[/accent]"


# ── raw ANSI (for the self-painted banner) ──────────────────────────────────
def _to_256(r: int, g: int, b: int) -> int:
    """Nearest xterm-256 index — colour cube or grey ramp (port of percival)."""

    def cube(c: int) -> int:
        if c < 48:
            return 0
        if c < 115:
            return 1
        return (c - 35) // 40

    ri, gi, bi = cube(r), cube(g), cube(b)
    levels = (0, 95, 135, 175, 215, 255)
    cr, cg, cb = levels[ri], levels[gi], levels[bi]
    cube_idx = 16 + 36 * ri + 6 * gi + bi
    avg = (r + g + b) // 3
    grey_idx = 23 if avg > 238 else max(0, (avg - 3) // 10)
    grey_val = 8 + 10 * grey_idx
    d_cube = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
    d_grey = (r - grey_val) ** 2 + (g - grey_val) ** 2 + (b - grey_val) ** 2
    return 232 + grey_idx if d_grey < d_cube else cube_idx


def _rgb(hexstr: str) -> tuple[int, int, int]:
    h = hexstr.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def color_mode() -> str:
    """``"truecolor"``, ``"256"`` or ``"none"`` for the active console."""
    if not console.is_terminal or os.environ.get("NO_COLOR"):
        return "none"
    system = console.color_system  # standard / 256 / truecolor / windows / None
    if system == "truecolor":
        return "truecolor"
    if system is None:
        return "none"
    return "256"


def ansi_fg(hexstr: str, mode: str | None = None) -> str:
    """Raw foreground escape for a palette colour under the given colour mode."""
    if mode is None:
        mode = color_mode()
    if mode == "none":
        return ""
    r, g, b = _rgb(hexstr)
    if mode == "truecolor":
        return f"\x1b[38;2;{r};{g};{b}m"
    return f"\x1b[38;5;{_to_256(r, g, b)}m"
