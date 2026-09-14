"""The CVE2PoC startup banner.

A Rosé Pine light sweeps across the ``CVE2POC`` wordmark as the tool starts,
exactly like percival's — everything behind the crest is settled iris, the crest
is a bright text highlight, and the glyphs ahead of it sit dim until the light
reaches them. It only runs on a colour TTY; piping, ``NO_COLOR``, ``--no-anim``
or ``CVE2POC_NO_ANIM`` fall back to a static banner (or none at all).
"""

from __future__ import annotations

import os
import sys
import time

from CVE2PoC.core import theme
from CVE2PoC.core.theme import console

# ANSI Shadow wordmark, painted at runtime (never with literal colour here).
WORDMARK = [
    " ██████╗██╗   ██╗███████╗██████╗ ██████╗  ██████╗  ██████╗",
    "██╔════╝██║   ██║██╔════╝╚════██╗██╔══██╗██╔═══██╗██╔════╝",
    "██║     ██║   ██║█████╗   █████╔╝██████╔╝██║   ██║██║     ",
    "██║     ╚██╗ ██╔╝██╔══╝  ██╔═══╝ ██╔═══╝ ██║   ██║██║     ",
    "╚██████╗ ╚████╔╝ ███████╗███████╗██║     ╚██████╔╝╚██████╗",
    " ╚═════╝  ╚═══╝  ╚══════╝╚══════╝╚═╝      ╚═════╝  ╚═════╝",
]

_STEP = 4  # columns the crest advances each frame
_FRAME = 0.028  # seconds per frame


def _tagline() -> None:
    """The ❀ tagline and the twinkling palette dots, under the wordmark."""
    console.print(
        f"[accent]❀[/accent]  [subtle]{theme.TAGLINE}[/subtle]"
        f"  [dim]v{theme.VERSION}[/dim]",
        highlight=False,
    )
    dots = " ".join(
        f"[{c}]●[/{c}]" for c in ("love", "gold", "rose", "pine", "foam", "iris")
    )
    console.print(dots, highlight=False)
    console.print()


def _static(color: bool) -> None:
    for line in WORDMARK:
        if color:
            console.print(line, style="heading", markup=False, highlight=False)
        else:
            print(line)
    _tagline()


def _animate() -> None:
    """Diagonal Rosé Pine light sweep, then settle to the static wordmark."""
    p = theme.PALETTE
    mode = theme.color_mode()
    seq = {k: theme.ansi_fg(p[k], mode) for k in ("iris", "foam", "text", "rose", "hl_high")}
    width = max(len(line) for line in WORDMARK)
    n = len(WORDMARK)
    out = sys.stdout
    first = True
    band = 0
    while True:
        if not first:
            out.write(f"\x1b[{n}A")
        first = False
        for row, line in enumerate(WORDMARK):
            buf = []
            for col, ch in enumerate(line):
                if ch == " ":
                    buf.append(" ")
                    continue
                # Crest tilts by row so the sweep reads diagonal.
                d = (band - row) - col
                if d >= 6:
                    color = seq["iris"]  # settled
                elif d >= 3:
                    color = seq["foam"]
                elif d >= 0:
                    color = seq["text"]  # crest
                elif d >= -2:
                    color = seq["rose"]  # leading glow
                else:
                    color = seq["hl_high"]  # not yet lit
                buf.append(color)
                buf.append(ch)
            out.write("".join(buf) + "\x1b[0m\x1b[K\n")
        out.flush()
        if band > width + n + 6:
            break
        time.sleep(_FRAME)
        band += _STEP
    # Settle to the static bold banner.
    out.write(f"\x1b[{n}A")
    heading = seq["iris"]
    for line in WORDMARK:
        out.write(f"\x1b[1m{heading}{line}\x1b[0m\x1b[K\n")
    out.flush()
    _tagline()


def banner(animate: bool = True) -> None:
    """Show the banner. ``animate`` gates only the sweep, never the wordmark."""
    color = theme.color_mode() != "none"
    if os.environ.get("CVE2POC_NO_ANIM"):
        animate = False
    if animate and color and console.is_terminal:
        _animate()
    else:
        _static(color)
