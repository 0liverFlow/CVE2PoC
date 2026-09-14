from rich import box
from rich.markup import escape
from rich.table import Table

from CVE2PoC.core.theme import poc_header

# 2025 CWE Top 25 Most Dangerous Software Weaknesses — flagged as high-attention.
CWE_TOP_25 = {
    "CWE-79", "CWE-89", "CWE-352", "CWE-862", "CWE-787", "CWE-22", "CWE-416",
    "CWE-125", "CWE-78", "CWE-94", "CWE-120", "CWE-434", "CWE-476", "CWE-121",
    "CWE-502", "CWE-122", "CWE-863", "CWE-20", "CWE-284", "CWE-200", "CWE-306",
    "CWE-918", "CWE-77", "CWE-639", "CWE-770",
}

# Severity → Rosé Pine ramp (foam → gold → rose → love).
SEVERITY_STYLES = {
    "LOW": "sev.low",
    "MEDIUM": "sev.medium",
    "HIGH": "sev.high",
    "CRITICAL": "sev.critical",
}


def display_cve_info(cve_record):
    """
    This function takes the cve_record and returns a table containing the different information related to the CVE ID submitted by the user.

    :param cve_record: This is a dictionary containing the CVE ID's information
    """

    base_score = cve_record["base_score"]
    if base_score != "N/A":
        if base_score < 4:
            base_score = f"[sev.low]{cve_record['base_score']}[/sev.low]"
        elif base_score < 7:
            base_score = f"[sev.medium]{cve_record['base_score']}[/sev.medium]"
        elif base_score < 9:
            base_score = f"[sev.high]{cve_record['base_score']}[/sev.high]"
        else:
            base_score = f"[sev.critical]{cve_record['base_score']}[/sev.critical]"

    epss_score = cve_record["epss_score"]
    if epss_score != "N/A":
        if epss_score >= 70:
            epss_score = f"[error]{cve_record['epss_score']}%[/error]"
        elif epss_score >= 40:
            epss_score = f"[warn]{cve_record['epss_score']}%[/warn]"
        else:
            epss_score = f"[foam]{cve_record['epss_score']}%[/foam]"

    severity_style = SEVERITY_STYLES.get(cve_record["severity"], "")
    if severity_style:
        severity = f"[{severity_style}]{cve_record['severity']}[/{severity_style}]"
    else:
        severity = cve_record["severity"]

    if cve_record.get("cwe", None) is not None:
        if cve_record["cwe"]:
            cwes = []
            for cwe in cve_record["cwe"]:
                # Highlight CWEs in the 2025 CWE Top 25 in gold, the rest in foam.
                if cwe in CWE_TOP_25:
                    cwes.append(f"[warn]{cwe}[/warn]")
                else:
                    cwes.append(f"[foam]{cwe}[/foam]")
            cwe = ",".join(cwes)
        else:
            cwe = "N/A"
    else:
        cwe = "N/A"

    if cve_record["kev"] == "Yes":
        kev = "[error]Yes[/error]"
    else:
        kev = cve_record["kev"]

    table = Table(
        show_lines=True,
        box=box.ROUNDED,
        border_style="muted",
        header_style="heading",
        title=cve_record["cve_id"],
        title_style="bold accent",
        title_justify="center",
    )
    table.add_column("Publication Date", justify="center")
    table.add_column("Severity", justify="center")
    table.add_column("Base Score", justify="center")
    table.add_column("EPSS", justify="center")
    table.add_column("Vendor", justify="center")
    table.add_column("Affected Product", justify="center")
    table.add_column("CISA KEV", justify="center")
    table.add_column("CWE", justify="center")
    table.add_column("Vector String", overflow="fold", justify="center")
    table.add_row(
        cve_record["publication_date"],
        severity,
        base_score,
        epss_score,
        cve_record["vendor"],
        cve_record["affected_product"],
        kev,
        cwe,
        cve_record["vector_string"],
    )
    return table


def display_poc_info(poc, poc_title, gh_api_key):
    """
    This function returns a PoC's information (description, clone URL, stargazers, forks, programming language) in a nice format

    :param poc: This is a dictionary containing the exploit/PoC's information like its description, clone url, stars, forks, programming language, etc.
    :param poc_title: This is the PoC title to display
    :param gh_api_key: This is your GitHub API key
    """
    description = poc["description"] if poc["description"] is not None else "N/A"
    lines = [
        poc_header(poc_title),
        f"[subtle]Description:[/subtle] {escape(str(description))}",
        f"[subtle]Clone URL:[/subtle]   [link]{escape(str(poc['html_url']))}[/link]",
        (
            f"[subtle]Stars:[/subtle] [gold]{poc['stargazers_count']}[/gold]"
            f"   [subtle]Forks:[/subtle] [gold]{poc['forks']}[/gold]"
        ),
    ]
    # The programming language is only present when a valid API key was given or
    # the GitHub rate limit was not reached.
    if not (poc["programming_language"] == "N/A" and gh_api_key is None):
        lines.append(
            f"[subtle]Language:[/subtle] [accent]{escape(str(poc['programming_language']))}[/accent]"
        )
    return "\n".join(lines)
