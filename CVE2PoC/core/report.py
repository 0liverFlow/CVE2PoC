import json
from datetime import datetime

from CVE2PoC.core.cve import (
    is_kev,
    check_cve_id_format,
    retrieve_cve_info_from_cve_org,
    get_epss,
)
from CVE2PoC.core.exploits import (
    search_github_exploits,
    search_exploits_from_other_sources,
)


def generate_json_report(data, output_dir_path):
    """
    This function generates a JSON report containing CVE IDs information

    :param data: A dictionary containing CVE IDs information
    :param output_dir_path: Ouptut directory to store the JSON report
    """
    with open(
        f"{output_dir_path}/cve2poc_report_{str(datetime.now().date()).replace('-', '_')}_{datetime.now().strftime('%H:%M:%S').replace(':', '_')}.json",
        "w",
    ) as f:
        json.dump(data, f, indent=4)
        return True
    return False


def generate_html_report(data, output_dir_path):
    """
    This function generates a HTML report containing CVE IDs information.

    The report is painted in Rosé Pine — Main, Moon and Dawn ship together with an
    in-page switcher, and the default follows the viewer's OS light/dark setting.

    :param data: A dictionary containing CVE IDs information
    :param output_dir_path: Ouptut directory to store the HTML report
    """
    report_date, report_time = (
        datetime.now().date(),
        datetime.now().strftime("%H:%M:%S"),
    )

    head = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>CVE2PoC Report</title>

        <!-- jQuery -->
        <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>

        <!-- DataTables CSS & JS -->
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    """

    style = """
        <style>
            /* ── Rosé Pine palettes ─────────────────────────────────────── */
            :root, :root[data-theme="main"] {
                --base:#191724; --surface:#1f1d2e; --overlay:#26233a;
                --muted:#6e6a86; --subtle:#908caa; --text:#e0def4;
                --love:#eb6f92; --gold:#f6c177; --rose:#ebbcba;
                --pine:#31748f; --foam:#9ccfd8; --iris:#c4a7e7;
                --hl-med:#403d52; --hl-high:#524f67;
            }
            :root[data-theme="moon"] {
                --base:#232136; --surface:#2a273f; --overlay:#393552;
                --muted:#6e6a86; --subtle:#908caa; --text:#e0def4;
                --love:#eb6f92; --gold:#f6c177; --rose:#ea9a97;
                --pine:#3e8fb0; --foam:#9ccfd8; --iris:#c4a7e7;
                --hl-med:#44415a; --hl-high:#56526e;
            }
            :root[data-theme="dawn"] {
                --base:#faf4ed; --surface:#fffaf3; --overlay:#f2e9e1;
                --muted:#9893a5; --subtle:#797593; --text:#575279;
                --love:#b4637a; --gold:#ea9d34; --rose:#d7827e;
                --pine:#286983; --foam:#56949f; --iris:#907aa9;
                --hl-med:#dfdad9; --hl-high:#cecacd;
            }
            /* Follow the OS when nothing is chosen: light → Dawn. */
            @media (prefers-color-scheme: light) {
                :root:not([data-theme]) {
                    --base:#faf4ed; --surface:#fffaf3; --overlay:#f2e9e1;
                    --muted:#9893a5; --subtle:#797593; --text:#575279;
                    --love:#b4637a; --gold:#ea9d34; --rose:#d7827e;
                    --pine:#286983; --foam:#56949f; --iris:#907aa9;
                    --hl-med:#dfdad9; --hl-high:#cecacd;
                }
            }

            html { color-scheme: dark light; }
            body {
                font-family: 'Inter', system-ui, sans-serif;
                background: var(--base);
                color: var(--text);
                margin: 0;
                padding: 0 40px 72px;
                transition: background .2s ease, color .2s ease;
            }
            a { text-decoration: none; color: var(--iris); }
            a:hover { text-decoration: underline; }

            /* ── Header ─────────────────────────────────────────────────── */
            .report-header { margin: 40px 0 26px; }
            .report-title {
                font-size: 30px; font-weight: 700; margin: 0;
                letter-spacing: .5px; color: var(--text);
            }
            .title-flower { color: var(--rose); margin-right: 6px; }
            .report-subtitle { font-size: 14px; color: var(--subtle); margin-top: 6px; }
            .report-rule {
                height: 3px; width: 260px; border-radius: 2px; margin-top: 16px;
                background: linear-gradient(90deg,
                    var(--pine), var(--foam), var(--iris), var(--rose), var(--gold));
            }

            /* ── Theme switcher ─────────────────────────────────────────── */
            .theme-switch-wrap { position: absolute; top: 40px; right: 40px; }
            .theme-switch {
                display: inline-flex; gap: 4px; padding: 4px;
                background: var(--surface); border: 1px solid var(--hl-med);
                border-radius: 12px;
            }
            .theme-switch button {
                border: none; background: transparent; color: var(--subtle);
                width: 34px; height: 30px; border-radius: 8px; cursor: pointer;
                font-size: 15px; line-height: 1; transition: all .15s ease;
            }
            .theme-switch button:hover { color: var(--text); background: var(--overlay); }
            .theme-switch button.active {
                color: var(--iris);
                background: color-mix(in srgb, var(--iris) 20%, transparent);
                box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--iris) 45%, transparent);
            }

            /* ── Pills ──────────────────────────────────────────────────── */
            .badge, .cvss-badge, .epss-badge {
                display: inline-block; border-radius: 6px; font-weight: 700;
                font-size: 13px; border: 1px solid transparent;
            }
            .badge { padding: 3px 9px; }
            .cvss-badge, .epss-badge { padding: 4px 9px; min-width: 38px; text-align: center; }
            .badge a { color: inherit; text-decoration: none; font-weight: inherit; }

            .badge.yes {
                color: var(--foam);
                background: color-mix(in srgb, var(--foam) 16%, transparent);
                border-color: color-mix(in srgb, var(--foam) 40%, transparent);
            }
            .badge.no {
                color: var(--muted);
                background: color-mix(in srgb, var(--muted) 14%, transparent);
                border-color: color-mix(in srgb, var(--muted) 30%, transparent);
            }

            .cvss-critical, .epss-high {
                color: var(--love);
                background: color-mix(in srgb, var(--love) 20%, transparent);
                border-color: color-mix(in srgb, var(--love) 45%, transparent);
            }
            .cvss-high {
                color: var(--rose);
                background: color-mix(in srgb, var(--rose) 20%, transparent);
                border-color: color-mix(in srgb, var(--rose) 45%, transparent);
            }
            .cvss-medium, .epss-medium {
                color: var(--gold);
                background: color-mix(in srgb, var(--gold) 20%, transparent);
                border-color: color-mix(in srgb, var(--gold) 45%, transparent);
            }
            .cvss-low, .epss-low {
                color: var(--foam);
                background: color-mix(in srgb, var(--foam) 18%, transparent);
                border-color: color-mix(in srgb, var(--foam) 42%, transparent);
            }
            .cvss-na {
                color: var(--muted);
                background: color-mix(in srgb, var(--muted) 14%, transparent);
                border-color: color-mix(in srgb, var(--muted) 30%, transparent);
            }

            /* ── Table ──────────────────────────────────────────────────── */
            table.dataTable {
                border: none !important;
                background: var(--surface) !important;
                border-radius: 12px;
            }
            table.dataTable thead th {
                cursor: pointer;
                border-bottom: 2px solid var(--hl-med) !important;
            }
            thead th {
                position: sticky; top: 0; z-index: 2;
                background: var(--overlay) !important;
                color: var(--iris) !important;
                font-weight: 600;
            }
            table.dataTable tbody tr,
            table.dataTable tbody tr.odd { background: var(--surface); }
            table.dataTable tbody tr.even {
                background: color-mix(in srgb, var(--overlay) 45%, var(--surface));
            }
            table.dataTable tbody tr:hover { background: var(--overlay) !important; }
            table.dataTable tbody td {
                border-top: 1px solid var(--hl-med) !important;
                color: var(--text);
            }
            tfoot { display: table-header-group; }

            td.vector-string {
                word-break: break-all; max-width: 350px; white-space: normal;
                color: var(--subtle); font-size: 12.5px;
            }

            /* ── Footer filter row ──────────────────────────────────────── */
            .filter-row th {
                background: var(--overlay);
                padding: 8px;
                border-bottom: 1px solid var(--hl-med);
            }
            .filter-row input, .filter-row select, tfoot select {
                width: 100%; padding: 6px 8px; font-size: 12px;
                border: 1px solid var(--hl-med); border-radius: 6px;
                background: var(--surface); color: var(--text);
                font-family: inherit;
            }
            .filter-row input:focus, .filter-row select:focus {
                outline: none; border-color: var(--iris);
            }
            .filter-row input::placeholder { color: var(--muted); }

            /* ── Reset button ───────────────────────────────────────────── */
            .reset-container { display: flex; justify-content: flex-end; align-items: center; }
            .reset-btn {
                padding: 6px 14px; font-size: 13px; font-weight: 600; cursor: pointer;
                border-radius: 8px; margin-left: 10px; border: 1px solid transparent;
                color: var(--iris);
                background: color-mix(in srgb, var(--iris) 16%, transparent);
                border-color: color-mix(in srgb, var(--iris) 38%, transparent);
            }
            .reset-btn:hover { background: color-mix(in srgb, var(--iris) 26%, transparent); }

            /* ── DataTables chrome ──────────────────────────────────────── */
            .dataTables_wrapper .dataTables_length,
            .dataTables_wrapper .dataTables_filter,
            .dataTables_wrapper .dataTables_info { color: var(--subtle); }
            .dataTables_wrapper .dataTables_length select,
            .dataTables_wrapper .dataTables_filter input {
                background: var(--surface); color: var(--text);
                border: 1px solid var(--hl-med); border-radius: 6px; padding: 4px 8px;
            }
            .dataTables_wrapper .dataTables_length select:focus,
            .dataTables_wrapper .dataTables_filter input:focus {
                outline: none; border-color: var(--iris);
            }
            .dataTables_wrapper .dataTables_paginate .paginate_button {
                color: var(--subtle) !important; border: none !important;
            }
            .dataTables_wrapper .dataTables_paginate .paginate_button:hover {
                color: var(--text) !important;
                background: var(--overlay) !important;
                border: 1px solid var(--hl-med) !important;
            }
            .dataTables_wrapper .dataTables_paginate .paginate_button.current,
            .dataTables_wrapper .dataTables_paginate .paginate_button.current:hover {
                color: var(--iris) !important;
                background: color-mix(in srgb, var(--iris) 18%, transparent) !important;
                border: 1px solid color-mix(in srgb, var(--iris) 40%, transparent) !important;
                border-radius: 6px;
            }

            /* ── Page footer ────────────────────────────────────────────── */
            #pageFooter {
                position: fixed; bottom: 0; left: 0; right: 0; text-align: center;
                padding: 11px 0; font-size: .82em;
                background: var(--surface); color: var(--subtle);
                border-top: 1px solid var(--hl-med);
            }
            .foot-flower { color: var(--rose); }
            .foot-sep { color: var(--muted); margin: 0 6px; }
        </style>
    """

    body_open = f"""
    </head>
    <body>
        <div class="theme-switch-wrap">
            <div class="theme-switch" role="group" aria-label="Theme">
                <button data-theme="main" title="Rosé Pine">◐</button>
                <button data-theme="moon" title="Rosé Pine Moon">☾</button>
                <button data-theme="dawn" title="Rosé Pine Dawn">☀</button>
            </div>
        </div>
        <div class="report-header">
            <h1 class="report-title"><span class="title-flower">❀</span>CVE2PoC Report</h1>
            <div class="report-subtitle">Generated on {report_date} at {report_time}</div>
            <div class="report-rule"></div>
        </div>
        <table id="report" class="display" style="width:100%">
            <thead>
                <tr>
                    <th>CVE ID</th>
                    <th>CVSS</th>
                    <th>EPSS</th>
                    <th>KEV</th>
                    <th>CWE</th>
                    <th>Vector String</th>
                    <th>GitHub</th>
                    <th>ExploitDB</th>
                    <th>Metasploit</th>
                    <th>Nuclei</th>
                </tr>
            </thead>
            <tfoot>
            <tr class="filter-row">
                <th><input type="text" placeholder="CVE..." /></th>
                <th>
                    <select class="cvss-filter-footer">
                        <option value="">CVSS</option>
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                 </th>
                <th>
                    <select class="epss-filter-footer">
                        <option value="">EPSS</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                </th>
                <th>
                    <select>
                        <option value="">All</option>
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                    </select>
                </th>
                <th><input type="text" placeholder="CWE..." /></th>
                <th><input type="text" placeholder="Vector..." /></th>
                <th><select><option value="">All</option><option>Yes</option><option>No</option></select></th>
                <th><select><option value="">All</option><option>Yes</option><option>No</option></select></th>
                <th><select><option value="">All</option><option>Yes</option><option>No</option></select></th>
                <th><select><option value="">All</option><option>Yes</option><option>No</option></select></th>
            </tr>
            </tfoot>
            <tbody>
    """

    head_and_body = head + style + body_open

    footer = r"""
    </tbody>
    </table>
    <div id="pageFooter">
        <span class="foot-flower">❀</span> CVE2PoC · Rosé Pine
        <span class="foot-sep">·</span> themed for DΛΣMOΘΠ-SEC
        <span class="foot-sep">·</span> upstream by 0liverFlow
    </div>
    <!-- Custom JS -->
    <script>
        $.fn.dataTable.ext.search.push(function(settings, data) {

        let cvss = parseFloat(data[1]);
        let epss = parseFloat(data[2]);

        let cvssFilter = $('.cvss-filter-footer').val();
        let epssFilter = $('.epss-filter-footer').val();

        if (cvssFilter) {

            if (!isNaN(cvss)) {
                if (cvssFilter === "critical" && cvss < 9) return false;
                if (cvssFilter === "high" && (cvss < 7 || cvss >= 9)) return false;
                if (cvssFilter === "medium" && (cvss < 4 || cvss >= 7)) return false;
                if (cvssFilter === "low" && cvss >= 4) return false;
            }
        }

        if (epssFilter) {
            if (epssFilter === "high" && epss < 70) return false;
            if (epssFilter === "medium" && (epss < 40 || epss >= 70)) return false;
            if (epssFilter === "low" && epss >= 40) return false;
        }

        return true;
    });

    $(document).ready(function() {
        var table = $('#report').DataTable({
            pageLength: 50,
            lengthMenu: [25, 50, 100, 200, 500],
            order: [[1, "desc"]],

            dom: '<"top"l<"reset-container">>rt<"bottom"ip><"clear">',

            autoWidth: false,

            columnDefs: [
                {
                    targets: 0,
                    render: function(data, type) {
                        if (type === 'sort' || type === 'type') {
                            let parts = data.split('-');
                            let year = parseInt(parts[1]) || 0;
                            let id = parseInt(parts[2]) || 0;
                            return year * 100000 + id;
                        }
                        return data;
                    }
                },
                {
                    targets: 1,
                    width: "60px",
                    render: function(data, type) {
                        if (type === 'sort' || type === 'type') {
                            return data === "N/A" ? -1 : parseFloat(data);
                        }
                        let cls = getCvssClass(data);
                        return `<span class="cvss-badge ${cls}">${data}</span>`;
                    }
                },
                {
                targets: 2,
                width: "60px",
                    render: function(data, type) {

                        let value = parseFloat(data);

                        if (type === 'sort' || type === 'type') {
                            return isNaN(value) ? -1 : value;
                        }

                        let cls = "";

                        if (value >= 70) {
                            cls = "epss-high";
                        } else if (value >= 40) {
                            cls = "epss-medium";
                        } else {
                            cls = "epss-low";
                        }

                        return `<span class="epss-badge ${cls}">${data}</span>`;
                    }
                },
                {
                    targets: 4,
                    width: "75px",
                        render: function(data, type) {

                            if (type === 'filter') {
                                return data.replace(/<[^>]*>/g, '');
                            }

                            if (type === 'sort' || type === 'type') {
                                let clean = data.replace(/<[^>]*>/g, '');
                                return parseInt(clean.replace('CWE-', '')) || 0;
                            }

                            return data;
                        }
                },
                {
                    targets: 6,
                    render: function(data, type) {

                        let match = data.match(/\((\d+)\)/);
                        let num = match ? parseInt(match[1]) : 0;

                        if (type === 'sort' || type === 'type') {
                            return num;
                        }

                        if (type === 'filter') {
                            return num > 0 ? 'Yes' : 'No';
                        }

                        return data;
                    }
                }

            ],

            initComplete: function () {
                var api = this.api();

                api.columns().every(function () {
                    var column = this;

                    $('input, select', column.footer()).on('keyup change', function () {
                        column.search(this.value).draw();
                    });
                });

                $(document).on('change', '.cvss-filter-footer, .epss-filter-footer', function () {
                    api.draw();
                });

                $('.reset-container').html(`
                    <button id="resetFilters" class="reset-btn">Reset</button>
                `);

                $('#resetFilters').on('click', function() {

                    $('#report tfoot input').val('');

                    $('#report tfoot select').prop('selectedIndex', 0);

                    $('.cvss-filter-footer').val('');
                    $('.epss-filter-footer').val('');

                    table.search('').columns().search('').draw();
                });

                $('.cvss-filter-footer, .epss-filter-footer').on('change', function () {
                    table.draw();
                });
            }
        });

    });

    // ── Rosé Pine theme switcher ──────────────────────────────────────────
    function applyTheme(t) {
        document.documentElement.setAttribute('data-theme', t);
        document.querySelectorAll('.theme-switch button').forEach(function(b) {
            b.classList.toggle('active', b.dataset.theme === t);
        });
        try { localStorage.setItem('cve2poc-theme', t); } catch (e) {}
    }

    (function () {
        var saved = null;
        try { saved = localStorage.getItem('cve2poc-theme'); } catch (e) {}
        if (!saved) {
            saved = (window.matchMedia &&
                     window.matchMedia('(prefers-color-scheme: light)').matches)
                ? 'dawn' : 'main';
        }
        applyTheme(saved);
        document.querySelectorAll('.theme-switch button').forEach(function(b) {
            b.addEventListener('click', function () { applyTheme(b.dataset.theme); });
        });
    })();

    function getCvssClass(score) {
        if (score === "N/A" || score === "") return "cvss-na";
        score = parseFloat(score);
        if (score >= 9.0) return "cvss-critical";
        if (score >= 7.0) return "cvss-high";
        if (score >= 4.0) return "cvss-medium";
        return "cvss-low";
    }
    </script>
    </body>
    </html>
    """

    for cve, cve_data in data.items():
        if cve_data["PoCs"]["GitHub"] != "No":
            if "nomi-sec" in cve_data["PoCs"]["GitHub"][0]:
                gh_td = f"<td><span class='badge yes'><a href='https://poc-in-github.motikan2010.net/api/v1/?cve_id={cve}' target='_blank'>Yes ({cve_data['PoCs']['GitHub'][-1]})</a></span></td>"
            else:
                gh_td = f"<td><span class='badge yes'><a href='https://github.com/trickest/cve/blob/main{cve_data['PoCs']['GitHub'][0].split('main')[-1]}' target='_blank'>Yes ({cve_data['PoCs']['GitHub'][-1]})</a></span></td>"
        else:
            gh_td = "<td><span class='badge no'>No</a></span></td>"
        if cve_data["PoCs"]["ExploitDB"] != "No":
            exploit_db_td = f"<td><span class='badge yes'><a href='{cve_data['PoCs']['ExploitDB']}' target='_blank'>Yes</a></span></td>"
        else:
            exploit_db_td = "<td><span class='badge no'>No</a></span></td>"
        if cve_data["PoCs"]["Metasploit"] != "No":
            msf_td = f"<td><span class='badge yes'><a href='{cve_data['PoCs']['Metasploit']}' target='_blank'>Yes</a></span></td>"
        else:
            msf_td = "<td><span class='badge no'>No</a></span></td>"
        if cve_data["PoCs"]["Nuclei"] != "No":
            nuclei_td = f"<td><span class='badge yes'><a href='{cve_data['PoCs']['Nuclei']}' target='_blank'>Yes</a></span></td>"
        else:
            nuclei_td = "<td><span class='badge no'>No</a></span></td>"

        if len(cve_data["CWE"].split(",")) > 1:
            cwes = cve_data["CWE"].split(",")
            cwe_td = "<td>"
            for cwe in cwes:
                if cwe == cwes[-1]:
                    cwe_td += f"<a href='https://cwe.mitre.org/data/definitions/{cwe.split('-')[-1]}.html' target='_blank'>{cwe}</a>"
                else:
                    cwe_td += f"<a href='https://cwe.mitre.org/data/definitions/{cwe.split('-')[-1]}.html' target='_blank'>{cwe}, </a>"
            cwe_td += "</td>"
        elif cve_data["CWE"] != "N/A":
            cwe_td = f"<td><a href='https://cwe.mitre.org/data/definitions/{cve_data['CWE'].split('-')[-1]}.html' target='_blank'>{cve_data['CWE']}</a></td>"
        else:
            cwe_td = "<td>N/A</td>"

        head_and_body += f"""
        <tr>
            <td><a href='https://nvd.nist.gov/vuln/detail/{cve}' target='_blank'>{cve}</a></td>
            <td>{cve_data["Base Score"]}</td>
            <td>{cve_data["EPSS"]}</td>
            <td>{cve_data["KEV"]}</td>
            {cwe_td}
            <td class="vector-string">{cve_data["Vector String"]}</td>
            {gh_td}
            {exploit_db_td}
            {msf_td}
            {nuclei_td}
        </tr>
        """
    html_report = head_and_body + footer

    with open(
        f"{output_dir_path}/cve2poc_report_{str(datetime.now().date()).replace('-', '_')}_{datetime.now().strftime('%H:%M:%S').replace(':', '_')}.html",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(html_report)
        return True
    return False


def get_cve_record_and_exploits(cve_id, headers, kevs, epss_data, exploits_db):
    """
    This function retrieves cve_record and exploits related to a CVE ID

    :param headers: HTTP headers used to send requests to GitHub API and Cve.org
    :param kevs: A dictionary containing KEVs
    :param epss_data: A list containing EPSS scores
    :param exploits_db: This stores Nuclei templates, Metasploit and Exploit-DB exploits databases
    :param cve_id: The CVE ID
    """
    github_headers = headers[0]
    # Checking whether the submitted CVE is valid or not
    if not check_cve_id_format(cve_id):
        return None, f"Skipping {cve_id}: Incorrect CVE ID"

    cve_record = retrieve_cve_info_from_cve_org(cve_id, headers)
    if cve_record is None:
        return None, f"No record found for {cve_id}!"

    # Checking if CVE is a KEV
    kev_status, _ = is_kev(kevs, cve_id)
    if kev_status == "Yes":
        cve_record["kev"] = "Yes"
    else:
        cve_record["kev"] = "No"

    # Retrieving EPSS score
    cve_record["epss"] = get_epss(cve_id, epss_data)
    # Pass msf_modules_db_json, exploit_db_csv, nuclei_db_json as function arguments or try to import them
    # exploits_db is a tuple
    msf_modules_db_json, exploit_db_csv, nuclei_db_json = exploits_db
    pocs_from_other_sources = search_exploits_from_other_sources(
        cve_id, msf_modules_db_json, exploit_db_csv, nuclei_db_json
    )
    gh_pocs, poc_url = search_github_exploits(cve_id, github_headers)

    return {
        "cve_id": cve_id,
        "cve_record": cve_record,
        "pocs_from_other_sources": pocs_from_other_sources,
        "github_pocs": (gh_pocs, poc_url),
    }, None
