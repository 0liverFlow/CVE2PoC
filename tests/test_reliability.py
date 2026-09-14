"""Tests for the non-visual reliability layer: HTTP session, cache, XDG config."""

from CVE2PoC.core import cache, config, http


# ── HTTP session ────────────────────────────────────────────────────────────
def test_session_has_timeout_and_retries():
    adapter = http.SESSION.get_adapter("https://example.com")
    assert adapter._timeout == http.DEFAULT_TIMEOUT
    retry = adapter.max_retries
    assert retry.total == 3
    for code in (429, 500, 502, 503, 504):
        assert code in retry.status_forcelist


def test_get_post_head_exist():
    for name in ("get", "post", "head"):
        assert callable(getattr(http, name))


# ── XDG config ──────────────────────────────────────────────────────────────
def test_xdg_paths_follow_env(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    assert config.config_dir() == tmp_path / "cfg" / "cve2poc"
    assert config.cache_dir() == tmp_path / "cache" / "cve2poc"
    assert config.env_file() == tmp_path / "cfg" / "cve2poc" / ".env"


def test_legacy_env_migration(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    legacy = tmp_path / "legacy.env"
    legacy.write_text("GITHUB_API_TOKEN=abc\n")
    monkeypatch.setattr(config, "legacy_env_file", lambda: legacy)

    assert config.migrate_legacy_env() is True
    assert config.env_file().exists()
    assert not legacy.exists()
    # idempotent: a second call is a no-op
    assert config.migrate_legacy_env() is False


# ── Feed cache ──────────────────────────────────────────────────────────────
def _no_network(monkeypatch):
    def boom(*a, **k):
        raise http.RequestException("offline")

    monkeypatch.setattr(cache.http, "get", boom)


def test_fresh_cache_is_reused_without_network(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "cache_dir", lambda: tmp_path)
    _no_network(monkeypatch)
    cache.configure(enabled=True, refresh=False, ttl_hours=24)
    (tmp_path / "feed.txt").write_text("CACHED")
    assert cache.cached_text("feed.txt", "https://unused/") == "CACHED"


def test_refresh_falls_back_to_stale_when_offline(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "cache_dir", lambda: tmp_path)
    _no_network(monkeypatch)
    (tmp_path / "feed.txt").write_text("STALE")
    cache.configure(enabled=True, refresh=True)
    assert cache.cached_text("feed.txt", "https://unused/") == "STALE"


def test_no_cache_ignores_file_and_returns_none_offline(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "cache_dir", lambda: tmp_path)
    _no_network(monkeypatch)
    (tmp_path / "feed.txt").write_text("CACHED")
    cache.configure(enabled=False)
    assert cache.cached_text("feed.txt", "https://unused/") is None
    cache.configure(enabled=True)  # reset shared state for other tests


def test_clear_removes_files(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "cache_dir", lambda: tmp_path)
    (tmp_path / "a.txt").write_text("1")
    (tmp_path / "b.txt").write_text("2")
    assert cache.clear() == 2
