from CVE2PoC.core import banner
from CVE2PoC.core.cve import check_cve_id_format
from CVE2PoC.core.report import generate_html_report


def test_cve_id_format():
    assert check_cve_id_format("CVE-2021-4104")
    assert check_cve_id_format("cve-2025-55182")  # case-insensitive
    assert not check_cve_id_format("2021-4104")
    assert not check_cve_id_format("CVE-2021")
    assert not check_cve_id_format("CVE-2021-4104-extra")


def _sample():
    return {
        "CVE-2025-55182": {
            "Publication Date": "2025-08-14",
            "Severity": "CRITICAL",
            "Base Score": 9.8,
            "EPSS": 94.2,
            "KEV": "Yes",
            "Vendor": "acme",
            "Affected Product": "widget",
            "CWE": "CWE-502",
            "Vector String": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            "PoCs": {
                "GitHub": ("https://poc-in-github.motikan2010.net/x nomi-sec", 7),
                "Metasploit": "No",
                "ExploitDB": "No",
                "Nuclei": "No",
            },
        }
    }


def test_html_report_is_rose_pine_with_switcher(tmp_path):
    assert generate_html_report(_sample(), str(tmp_path)) is True
    html = next(tmp_path.glob("cve2poc_report_*.html")).read_text(encoding="utf-8")
    for variant in ('data-theme="main"', 'data-theme="moon"', 'data-theme="dawn"'):
        assert variant in html
    assert "color-mix(" in html                 # theme-robust pills
    assert "function applyTheme" in html        # switcher wired
    assert "prefers-color-scheme" in html       # follows OS setting
    assert "CVE-2025-55182" in html             # the row rendered


def test_banner_wordmark_and_static_fallback(capsys):
    assert len(banner.WORDMARK) == 6
    banner._static(color=False)  # no-colour path must not raise
    out = capsys.readouterr().out
    assert "from a CVE ID" in out               # tagline present
