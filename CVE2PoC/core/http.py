"""One shared, hardened HTTP session for the whole tool.

Every network call in CVE2PoC goes through here so it inherits three things the
raw ``requests.get`` calls never had:

* a **timeout** — a single slow or hung host can no longer stall the whole run,
* **connection pooling** — one keep-alive session instead of a fresh socket per
  request (noticeably faster across the many lookups a single CVE triggers),
* **retries with backoff** on transient failures (connection resets and
  429/5xx), honouring ``Retry-After``.

Drop-in: ``from CVE2PoC.core import http`` then ``http.get(url, headers=...)``.
Signatures match ``requests`` — extra kwargs (``params``, ``stream``,
``allow_redirects`` …) pass straight through, and a per-call ``timeout`` wins
over the default.
"""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# (connect, read) seconds. Read timeout is per-socket-read, so large feed
# downloads are fine as long as bytes keep arriving.
DEFAULT_TIMEOUT = (6, 30)

# Re-export so callers can `except http.RequestException`.
RequestException = requests.RequestException
Timeout = requests.Timeout
ConnectionError = requests.ConnectionError


class _TimeoutAdapter(HTTPAdapter):
    """An adapter that applies a default timeout when the caller omits one."""

    def __init__(self, *args, timeout=DEFAULT_TIMEOUT, **kwargs):
        self._timeout = timeout
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        if kwargs.get("timeout") is None:
            kwargs["timeout"] = self._timeout
        return super().send(request, **kwargs)


def build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        connect=3,
        read=2,
        status=2,
        backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD", "POST"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = _TimeoutAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


SESSION = build_session()


def get(url, **kwargs):
    return SESSION.get(url, **kwargs)


def post(url, **kwargs):
    return SESSION.post(url, **kwargs)


def head(url, **kwargs):
    return SESSION.head(url, **kwargs)
