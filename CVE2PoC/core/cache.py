"""A tiny on-disk cache for the big shared feeds (CISA KEV, EPSS, exploit DBs).

These feeds are the same for every CVE and are megabytes each, yet the tool used
to re-download all of them on every single invocation. Here we keep the raw
response body under ``~/.cache/cve2poc`` and reuse it while it is younger than a
TTL. Parsing is unchanged — callers still parse the text they get back.

If the network is down, a *stale* cache is used rather than failing outright, so
an offline lookup still works off yesterday's data. ``configure()`` wires up the
``--refresh`` / ``--no-cache`` flags.
"""

from __future__ import annotations

import time
from pathlib import Path

from CVE2PoC.core import config, http
from CVE2PoC.core.user_agent import get_user_agent

# Runtime knobs, set once from the CLI flags via configure().
_STATE = {"enabled": True, "refresh": False, "ttl_seconds": 24 * 3600}


def configure(*, enabled: bool = True, refresh: bool = False, ttl_hours: float = 24):
    _STATE["enabled"] = enabled
    _STATE["refresh"] = refresh
    _STATE["ttl_seconds"] = int(ttl_hours * 3600)


def _fresh(path: Path) -> bool:
    try:
        return (time.time() - path.stat().st_mtime) < _STATE["ttl_seconds"]
    except OSError:
        return False


def cached_text(name: str, url: str, *, headers: dict | None = None) -> str | None:
    """Return the body of ``url`` as text, served from cache when fresh.

    Order of preference: fresh cache → network (then cached) → stale cache.
    Returns ``None`` only when there is no cache and the fetch fails.
    """
    path = config.cache_dir() / name
    use_cache = _STATE["enabled"]

    if use_cache and not _STATE["refresh"] and _fresh(path):
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            pass

    try:
        resp = http.get(url, headers=headers or {"User-Agent": get_user_agent()})
        if resp.status_code == 200:
            if use_cache:
                try:
                    config.ensure_cache_dir()
                    path.write_text(resp.text, encoding="utf-8")
                except OSError:
                    pass
            return resp.text
    except http.RequestException:
        pass

    # Network failed or returned non-200 — fall back to a stale copy if we have one.
    if use_cache and path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return None
    return None


def clear() -> int:
    """Delete all cached feeds. Returns the number of files removed."""
    d = config.cache_dir()
    removed = 0
    if d.exists():
        for f in d.iterdir():
            if f.is_file():
                try:
                    f.unlink()
                    removed += 1
                except OSError:
                    pass
    return removed
