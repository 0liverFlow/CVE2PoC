"""Filesystem locations for CVE2PoC.

Secrets and cache used to live inside the installed package (``core/.env`` and
re-downloaded feeds), which meant every reinstall wiped your API keys and no
lookup was ever cached. Everything user-owned now lives under the XDG base
directories instead:

* config + secrets → ``$XDG_CONFIG_HOME/cve2poc`` (``~/.config/cve2poc``)
* cached feeds     → ``$XDG_CACHE_HOME/cve2poc``  (``~/.cache/cve2poc``)

``BASE_DIR`` still points at the package (it ships read-only data such as
``data/user_agents.txt``).
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

# The installed package directory — home of shipped, read-only data files.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP = "cve2poc"


def _xdg(env_var: str, default: str) -> Path:
    root = os.environ.get(env_var)
    base = Path(root) if root else Path.home() / default
    return base / APP


def config_dir() -> Path:
    return _xdg("XDG_CONFIG_HOME", ".config")


def cache_dir() -> Path:
    return _xdg("XDG_CACHE_HOME", ".cache")


def env_file() -> Path:
    """Where GitHub/NVD API keys are stored (survives reinstalls)."""
    return config_dir() / ".env"


def legacy_env_file() -> Path:
    """The old in-package location, kept only so we can migrate away from it."""
    return Path(BASE_DIR) / ".env"


def ensure_config_dir() -> Path:
    d = config_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def ensure_cache_dir() -> Path:
    d = cache_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def migrate_legacy_env() -> bool:
    """Move a pre-existing in-package .env to the XDG location, once.

    Returns True if a migration happened. Safe to call on every startup.
    """
    old, new = legacy_env_file(), env_file()
    if old.exists() and not new.exists():
        try:
            ensure_config_dir()
            shutil.copy2(old, new)
            old.unlink()
            return True
        except OSError:
            return False
    return False
