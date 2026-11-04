"""Generate QA deliverables from execution results.

Inputs
  --results          automation/reports/cucumber.json (optional; Cucumber JSON formatter output)
  --manual-results   reporting/manual_results.csv (optional; TC ID,Status,Actual Result,Defect ID,Executed By,Executed On)
  reporting/defect_log.json (always)

Outputs (deliverables/)
  execution_results.json          TC id -> merged status (feeds the RTM)
  OpsDesk_Test_Design_RTM.xlsx    rebuilt with execution columns filled
  OpsDesk_Defect_Summary.xlsx     defect log, issue register, automation failures to triage, summaries
  OpsDesk_QA_Status_Report.html   status report for stakeholders
"""
import argparse
import csv
import html
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "test-design"))
import opsdesk_test_data as d  # noqa: E402

OUT = ROOT / "deliverables"
FONT = "Arial"
HDR = PatternFill("solid", fgColor="1F3864")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
SEVERITIES = ["Critical", "High", "Medium", "Low"]
TODAY = datetime.now().strftime("%d-%b-%Y")


# ---------------------------------------------------------------------------
# Result collection
# ---------------------------------------------------------------------------
def scenario_status(element):
    statuses = [s.get("result", {}).get("status", "skipped") for s in element.get("steps", [])]
    if any(s in ("failed", "ambiguous") for s in statuses):
        return "failed"
    if statuses and all(s == "passed" for s in statuses):
        return "passed"
    return "skipped"  # skipped by a hook/step (missing credential or data), undefined or pending


def first_error(element):
    for s in element.get("steps", []):
        r = s.get("result", {})
        if r.get("status") == "failed":
            msg = (r.get("error_message") or "").strip().splitlines()
            return f"{s.get('keyword', '').strip()} {s.get('name', '')}: {msg[0] if msg else 'failed'}"[:500]
    return ""


def load_cucumber(path):
    """TC id -> list of scenario outcomes (scenario outlines produce one per example)."""
    runs = defaultdict(list)
    if not path or not Path(path).exists():
        return runs, None
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    run_time = datetime.fromtimestamp(Path(path).stat().st_mtime).strftime("%d-%b-%Y %H:%M")
    for feature in data:
        for el in feature.get("elements", []):
            if el.get("type") == "background":
                continue
            tags = [t["name"].lstrip("@") for t in el.get("tags", [])]
            for tc in (t for t in tags if t.startswith("TC-")):
                runs[tc].append({
                    "status": scenario_status(el),
                    "scenario": el.get("name", ""),
                    "feature": feature.get("uri", ""),
                    "error": first_error(el),
                })
    return runs, run_time


def merge_results(cucumber_runs, manual_csv, run_time):
    results = {}
    for tc, outcomes in cucumber_runs.items():
        st = [o["status"] for o in outcomes]
        if "failed" in st:
            status = "Fail"
            actual = "; ".join(o["error"] for o in outcomes if o["status"] == "failed")
        elif st and all(s == "passed" for s in st):
            status, actual = "Pass", "As expected (automated)"
        else:
            status, actual = "Blocked", "Skipped by automation (missing credential, test data or feature)"
        results[tc] = {"status": status, "actual": actual, "defect": "", "executed_by": "Automation", "date": run_time or TODAY}
    if manual_csv and Path(manual_csv).exists():
        with open(manual_csv, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                tc = (row.get("TC ID") or "").strip()
                if not tc:
                    continue
                results[tc] = {  # manual result overrides automation for the same case
                    "status": row.get("Status", "Not Run").strip(),
                    "actual": row.get("Actual Result", "").strip(),
                    "defect": row.get("Defect ID", "").strip(),
                    "executed_by": row.get("Executed By", "QA").strip(),
                    "date": row.get("Executed On", TODAY).strip(),
                }
    return results


def link_defects(results, defects):
    for df in defects:
        for tc in [t.strip() for t in df.get("tc", "").split(",") if t.strip()]:
            if tc in results and df["status"].lower() not in ("closed", "rejected"):
                existing = results[tc].get("defect", "")
                results[tc]["defect"] = ", ".join(x for x in [existing, df["id"]] if x)


# ---------------------------------------------------------------------------
# Defect summary workbook
# ---------------------------------------------------------------------------
def table(ws, start, headers, rows, widths):
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=start, column=i, value=h)
        c.font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
        c.fill = HDR
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = BORDER
    for r, row in enumerate(rows, start + 1):
        for i, v in enumerate(row, 1):
            c = ws.cell(row=r, column=i, value=v)
            if isinstance(v, str) and v.startswith("="):
                c.data_type = "s"
            c.font = Font(name=FONT, size=9)
            c.alignment = WRAP
            c.border = BORDER
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=start + 1, column=1)
    ws.auto_filter.ref = f"A{start}:{get_column_letter(len(headers))}{max(start + len(rows), start + 1)}"
    return start + len(rows)


def build_defect_workbook(defects, issues, cucumber_runs, path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws["A1"] = "OpsDesk — Defect Summary"
    ws["A1"].font = Font(name=FONT, bold=True, size=14, color="1F3864")
    ws["A2"] = f"Generated {TODAY}. Figures are formulas over 'Defect Log' and 'Issues & Blockers'."
    ws["A2"].font = Font(name=FONT, italic=True, size=9)

    statuses = ["Open", "In Progress", "Fixed", "Retest", "Closed", "Rejected"]
    ws["A4"] = "Severity \\ Status"
    for j, s in enumerate(statuses + ["Total"], 2):
        ws.cell(row=4, column=j, value=s)
    for i, sev in enumerate(SEVERITIES + ["Total"], 5):
        ws.cell(row=i, column=1, value=sev)
        for j, s in enumerate(statuses, 2):
            col = get_column_letter(j)
            if sev == "Total":
                ws.cell(row=i, column=j, value=f"=SUM({col}5:{col}8)")
            else:
                ws.cell(row=i, column=j, value=f"=COUNTIFS('Defect Log'!$E:$E,$A{i},'Defect Log'!$G:$G,{col}$4)")
        last = get_column_letter(len(statuses) + 1)
        ws.cell(row=i, column=len(statuses) + 2, value=f"=SUM(B{i}:{last}{i})")
    for c in ws[4]:
        c.font = Font(name=FONT, bold=True, color="FFFFFF")
        c.fill = HDR

    types = sorted({df["type"] for df in defects} | {"Functional", "Security", "UI", "Performance"})
    ws["A12"] = "Defects by type"
    ws["A12"].font = Font(name=FONT, bold=True)
    for i, t in enumerate(types, 13):
        ws.cell(row=i, column=1, value=t)
        ws.cell(row=i, column=2, value=f"=COUNTIF('Defect Log'!$C:$C,A{i})")
    r = 13 + len(types) + 1
    ws.cell(row=r, column=1, value="Product defects (Functional/Security/UI/Performance)").font = Font(name=FONT, bold=True)
    ws.cell(row=r, column=2, value="=" + "+".join(f"COUNTIF('Defect Log'!$C:$C,\"{t}\")" for t in ["Functional", "Security", "UI", "Performance"]))
    ws.cell(row=r + 1, column=1, value="Requirement / documentation findings").font = Font(name=FONT, bold=True)
    ws.cell(row=r + 1, column=2, value=f"=COUNTA('Defect Log'!A4:A1000)-B{r}")
    ws.cell(row=r + 2, column=1, value="Open blocking issues (Critical/High)").font = Font(name=FONT, bold=True)
    ws.cell(row=r + 2, column=2, value="=COUNTIFS('Issues & Blockers'!$E:$E,\"Critical\",'Issues & Blockers'!$F:$F,\"Open\")+COUNTIFS('Issues & Blockers'!$E:$E,\"High\",'Issues & Blockers'!$F:$F,\"Open\")")
    ws.cell(row=r + 3, column=1, value="Automation failures awaiting triage").font = Font(name=FONT, bold=True)
    ws.cell(row=r + 3, column=2, value="=COUNTA('Automation Failures'!A4:A1000)")
    ws.column_dimensions["A"].width = 46
    for col in "BCDEFGH":
        ws.column_dimensions[col].width = 12

    ws = wb.create_sheet("Defect Log")
    ws["A1"] = "Defect Log"
    ws["A1"].font = Font(name=FONT, bold=True, size=14, color="1F3864")
    rows = [[df["id"], df["title"], df["type"], df["module"], df["severity"], df["priority"], df["status"],
             df["req"], df["tc"], df["description"], df["expected"], df["actual"], df["found_in"],
             df["reported_by"], df["reported_on"], df.get("assigned_to", "")] for df in defects]
    last = table(ws, 3, ["Defect ID", "Title", "Type", "Module", "Severity", "Priority", "Status", "Req ID(s)", "TC ID(s)",
                         "Description", "Expected", "Actual", "Found In", "Reported By", "Reported On", "Assigned To"],
                 rows, [10, 40, 18, 8, 10, 8, 10, 12, 16, 60, 40, 40, 30, 11, 12, 18])
    rng = f"E4:E{max(last, 4)}"
    for sev, color in [("Critical", "FF0000"), ("High", "FFC7CE"), ("Medium", "FFEB9C"), ("Low", "DDEBF7")]:
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{sev}"'], fill=PatternFill("solid", fgColor=color)))

    ws = wb.create_sheet("Issues & Blockers")
    ws["A1"] = "Issues & Blockers (not product defects)"
    ws["A1"].font = Font(name=FONT, bold=True, size=14, color="1F3864")
    table(ws, 3, ["Issue ID", "Title", "Category", "Impact", "Severity", "Status", "Raised On", "Owner", "Action Needed"],
          [[i["id"], i["title"], i["category"], i["impact"], i["severity"], i["status"], i["raised_on"], i["owner"], i["action"]] for i in issues],
          [10, 46, 16, 50, 10, 9, 12, 16, 60])

    ws = wb.create_sheet("Automation Failures")
    ws["A1"] = "Automation Failures — triage each: product defect (log in defect_log.json) or script/locator issue"
    ws["A1"].font = Font(name=FONT, bold=True, size=12, color="1F3864")
    fails = [[tc, o["feature"], o["scenario"], o["error"], "To triage"]
             for tc, outs in sorted(cucumber_runs.items()) for o in outs if o["status"] == "failed"]
    table(ws, 3, ["TC ID", "Feature", "Scenario", "First Failing Step / Error", "Triage"], fails, [13, 30, 40, 90, 12])

    wb.calculation.fullCalcOnLoad = True
    wb.save(path)


# ---------------------------------------------------------------------------
# Status report (HTML)
# ---------------------------------------------------------------------------
def rag(exec_pct, pass_pct, open_blockers, open_crit_high_defects):
    if open_blockers or open_crit_high_defects:
        return "RED"
    if exec_pct < 0.8 or pass_pct < 0.95:
        return "AMBER"
    return "GREEN"


def build_status_report(results, defects, issues, run_time, path):
    tcs = d.TEST_CASES
    status_of = {c["id"]: results.get(c["id"], {}).get("status") or ("Blocked" if c["automation"] == d.BLOCKED else "Not Run") for c in tcs}
    counts = Counter(status_of.values())
    total = len(tcs)
    executed = counts["Pass"] + counts["Fail"]
    exec_pct = executed / total if total else 0
    pass_pct = counts["Pass"] / executed if executed else 0
    auto = Counter(c["automation"] for c in tcs)
    high = [c for c in tcs if c["priority"] == "High"]
    high_exec = sum(status_of[c["id"]] in ("Pass", "Fail") for c in high)
    product_types = {"Functional", "Security", "UI", "Performance"}
    open_defects = [x for x in defects if x["status"].lower() not in ("closed", "rejected")]
    open_product = [x for x in open_defects if x["type"] in product_types]
    open_findings = [x for x in open_defects if x["type"] not in product_types]
    open_ch = [x for x in open_product if x["severity"] in ("Critical", "High")]
    blockers = [i for i in issues if i["status"] == "Open" and i["severity"] in ("Critical", "High")]
    overall = rag(exec_pct, pass_pct, blockers, open_ch)

    by_module = []
    for code, (name, _) in d.MODULES.items():
        ids = [c["id"] for c in tcs if c["module"] == code]
        mc = Counter(status_of[i] for i in ids)
        by_module.append((name, len(ids), mc["Pass"], mc["Fail"], mc["Blocked"], mc["Not Run"]))

    req_rows = []
    for rid, title, *_ in d.REQUIREMENTS:
        ids = [c["id"] for c in tcs if rid in [x.strip() for x in c["req"].split(",")]]
        mc = Counter(status_of[i] for i in ids)
        state = "Failing" if mc["Fail"] else "Passed" if mc["Pass"] == len(ids) else "In progress" if mc["Pass"] else "Not executed"
        req_rows.append((rid, title, len(ids), mc["Pass"], mc["Fail"], state))
    req_state = Counter(r[5] for r in req_rows)

    e = html.escape
    sev_count = Counter(x["severity"] for x in open_defects)

    def bar(n, of):
        return 0 if not of else round(100 * n / of)

    module_html = "".join(
        f"<tr><td>{e(n)}</td><td class=num>{t}</td><td class=num>{p}</td><td class=num>{f}</td><td class=num>{b}</td><td class=num>{nr}</td>"
        f"<td><div class=stack><span class=s-pass style='width:{bar(p, t)}%'></span><span class=s-fail style='width:{bar(f, t)}%'></span>"
        f"<span class=s-block style='width:{bar(b, t)}%'></span></div></td></tr>"
        for n, t, p, f, b, nr in by_module)
    defect_html = "".join(
        f"<tr><td>{e(x['id'])}</td><td>{e(x['title'])}</td><td>{e(x['type'])}</td><td><span class='sev sev-{x['severity'].lower()}'>{e(x['severity'])}</span></td><td>{e(x['status'])}</td><td>{e(x.get('assigned_to', ''))}</td></tr>"
        for x in sorted(open_defects, key=lambda x: SEVERITIES.index(x["severity"])))
    issue_html = "".join(
        f"<tr><td>{e(i['id'])}</td><td><strong>{e(i['title'])}</strong><div class=muted>{e(i['impact'])}</div></td><td><span class='sev sev-{i['severity'].lower()}'>{e(i['severity'])}</span></td><td>{e(i['owner'])}</td><td>{e(i['action'])}</td></tr>"
        for i in issues if i["status"] == "Open")
    req_html = "".join(
        f"<tr><td>{e(r[0])}</td><td>{e(r[1])}</td><td class=num>{r[2]}</td><td class=num>{r[3]}</td><td class=num>{r[4]}</td><td>{e(r[5])}</td></tr>" for r in req_rows)

    exec_note = (f"Last automated run: {e(run_time)}." if run_time else
                 "No execution yet: the application URL has been unreachable (ngrok ERR_NGROK_3200) since 30-Oct-2026.")
    next_steps = [
        "Restore the application URL (ISS-001) and share it; update OPSDESK_BASE_URL.",
        "Run the @smoke suite headed to calibrate locators (ISS-005), then the full suite.",
        "Execute manual High-priority cases (SLA timing, alerts, auto-close, channels) and record results in reporting/manual_results.csv.",
        "Obtain Team lead and Super admin access (ISS-002) to unblock role and Administration cases.",
        "BA to answer requirement findings DEF-002, DEF-003 and DEF-004 (Medium).",
    ] if not executed else [
        "Triage every row in 'Automation Failures' (defect vs. script issue) and log product defects.",
        "Re-test fixed defects and re-run the regression suite.",
        "Close open Critical/High defects or agree workarounds before sign-off.",
        "Complete remaining manual High-priority cases.",
    ]

    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpsDesk QA Status</title>
<style>
:root{{--bg:#f6f7f9;--card:#fff;--ink:#1b1f24;--muted:#5b6470;--line:#e2e5ea;--accent:#1f3864;
--pass:#2e7d32;--fail:#c62828;--block:#ef6c00;--notrun:#9aa3ad;--red:#c62828;--amber:#b26a00;--green:#2e7d32}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#111418;--card:#1a1f25;--ink:#e8ebef;--muted:#9aa3ad;--line:#2b323a;--accent:#8fb0e8;
--pass:#66bb6a;--fail:#ef5350;--block:#ffa726;--notrun:#5f6873;--red:#ef5350;--amber:#ffb74d;--green:#66bb6a}}}}
:root[data-theme="dark"]{{--bg:#111418;--card:#1a1f25;--ink:#e8ebef;--muted:#9aa3ad;--line:#2b323a;--accent:#8fb0e8;
--pass:#66bb6a;--fail:#ef5350;--block:#ffa726;--notrun:#5f6873;--red:#ef5350;--amber:#ffb74d;--green:#66bb6a}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 16px 48px}}
h1{{font-size:24px;margin:0 0 4px}}h2{{font-size:17px;margin:28px 0 10px;color:var(--accent)}}
.muted{{color:var(--muted);font-size:12.5px}}
.head{{display:flex;flex-wrap:wrap;gap:12px;justify-content:space-between;align-items:flex-start}}
.rag{{padding:6px 14px;border-radius:999px;font-weight:700;color:#fff;letter-spacing:.04em}}
.rag-RED{{background:var(--red)}}.rag-AMBER{{background:var(--amber)}}.rag-GREEN{{background:var(--green)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}}
.kpi .v{{font-size:26px;font-weight:700}}.kpi .l{{color:var(--muted);font-size:12.5px}}
.wrap{{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px}}
table{{border-collapse:collapse;width:100%;min-width:560px}}th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-size:12px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.03em}}
td.num,th.num{{text-align:right;font-variant-numeric:tabular-nums}}
.stack{{display:flex;height:10px;border-radius:5px;overflow:hidden;background:var(--notrun);min-width:120px}}
.s-pass{{background:var(--pass)}}.s-fail{{background:var(--fail)}}.s-block{{background:var(--block)}}
.legend span{{display:inline-flex;align-items:center;gap:6px;margin-right:14px;font-size:12.5px;color:var(--muted)}}
.legend i{{width:10px;height:10px;border-radius:2px;display:inline-block}}
.sev{{padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600;border:1px solid currentColor}}
.sev-critical{{color:var(--red)}}.sev-high{{color:var(--fail)}}.sev-medium{{color:var(--amber)}}.sev-low{{color:var(--muted)}}
ul{{margin:6px 0;padding-left:20px}}
</style></head><body><main>
<div class=head><div><h1>OpsDesk — QA Status Report</h1>
<div class=muted>Report date {TODAY} · Build documented 28-Oct-2026 · Environment: ngrok test URL · {exec_note}</div></div>
<div class="rag rag-{overall}">{overall}</div></div>

<h2>Summary</h2>
<div class=card><ul>
<li>Test design complete: <strong>{total}</strong> test cases across <strong>{len(d.MODULES)}</strong> scenarios, tracing to all <strong>{len(d.REQUIREMENTS)}</strong> requirements (100% requirement coverage).</li>
<li>Automation (Playwright + Cucumber BDD): <strong>{auto[d.AUTO]}</strong> cases automated, <strong>{auto[d.BLOCKED]}</strong> automatable but blocked by access/feature gaps, <strong>{auto[d.MANUAL]}</strong> manual.</li>
<li>Execution: <strong>{executed}</strong> of {total} executed ({exec_pct:.0%}); pass rate {pass_pct:.0%} of executed; High priority executed {high_exec}/{len(high)}.</li>
<li>Defects: <strong>{len(open_product)}</strong> open product defects; <strong>{len(open_findings)}</strong> open requirement/documentation findings from static review.</li>
<li>Blocking issues: <strong>{len(blockers)}</strong> open Critical/High ({", ".join(e(b["id"]) for b in blockers) or "none"}).</li>
</ul></div>

<h2>Key figures</h2>
<div class=grid>
<div class="card kpi"><div class=v>{total}</div><div class=l>Test cases designed</div></div>
<div class="card kpi"><div class=v>{exec_pct:.0%}</div><div class=l>Executed ({executed}/{total})</div></div>
<div class="card kpi"><div class=v>{counts['Pass']}</div><div class=l>Passed</div></div>
<div class="card kpi"><div class=v>{counts['Fail']}</div><div class=l>Failed</div></div>
<div class="card kpi"><div class=v>{counts['Blocked']}</div><div class=l>Blocked</div></div>
<div class="card kpi"><div class=v>{len(open_product)}</div><div class=l>Open product defects</div></div>
<div class="card kpi"><div class=v>{auto[d.AUTO]}</div><div class=l>Automated cases</div></div>
<div class="card kpi"><div class=v>{req_state['Passed']}/{len(d.REQUIREMENTS)}</div><div class=l>Requirements fully passed</div></div>
</div>

<h2>Execution by module</h2>
<div class="legend"><span><i style="background:var(--pass)"></i>Pass</span><span><i style="background:var(--fail)"></i>Fail</span><span><i style="background:var(--block)"></i>Blocked</span><span><i style="background:var(--notrun)"></i>Not run</span></div>
<div class=wrap><table><thead><tr><th>Module</th><th class=num>Cases</th><th class=num>Pass</th><th class=num>Fail</th><th class=num>Blocked</th><th class=num>Not run</th><th>Progress</th></tr></thead><tbody>{module_html}</tbody></table></div>

<h2>Blocking issues and risks</h2>
<div class=wrap><table><thead><tr><th>ID</th><th>Issue</th><th>Severity</th><th>Owner</th><th>Action needed</th></tr></thead><tbody>{issue_html or "<tr><td colspan=5>None open</td></tr>"}</tbody></table></div>

<h2>Open defects and findings</h2>
<div class=muted>Open by severity: {", ".join(f"{s} {sev_count[s]}" for s in SEVERITIES)}</div>
<div class=wrap><table><thead><tr><th>ID</th><th>Title</th><th>Type</th><th>Severity</th><th>Status</th><th>Owner</th></tr></thead><tbody>{defect_html or "<tr><td colspan=6>None open</td></tr>"}</tbody></table></div>

<h2>Requirement traceability</h2>
<div class=wrap><table><thead><tr><th>Req</th><th>Requirement</th><th class=num>TCs</th><th class=num>Pass</th><th class=num>Fail</th><th>State</th></tr></thead><tbody>{req_html}</tbody></table></div>

<h2>Next steps</h2>
<div class=card><ul>{"".join(f"<li>{e(s)}</li>" for s in next_steps)}</ul></div>
<p class=muted>Source: deliverables/OpsDesk_Test_Design_RTM.xlsx, OpsDesk_Defect_Summary.xlsx; generated by reporting/generate_reports.py.</p>
</main></body></html>"""
    path.write_text(doc, encoding="utf-8")
    return overall, counts, executed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", help="Cucumber JSON (automation/reports/cucumber.json)")
    ap.add_argument("--manual-results", default=str(ROOT / "reporting" / "manual_results.csv"))
    ap.add_argument("--execution-results", help="rebuild from a saved execution_results.json instead of a Cucumber run")
    args = ap.parse_args()

    log = json.loads((ROOT / "reporting" / "defect_log.json").read_text(encoding="utf-8"))
    if args.execution_results:
        results = json.loads(Path(args.execution_results).read_text(encoding="utf-8"))
        for r in results.values():
            r["defect"] = ""  # re-linked from defect_log.json below
        runs, run_time = {}, next((r["date"] for r in results.values()), None)
    else:
        runs, run_time = load_cucumber(args.results)
        results = merge_results(runs, args.manual_results, run_time)
    link_defects(results, log["defects"])

    OUT.mkdir(exist_ok=True)
    res_path = OUT / "execution_results.json"
    res_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "test-design" / "build_test_design.py"), "--results", str(res_path)], check=True)
    build_defect_workbook(log["defects"], log["issues"], runs, OUT / "OpsDesk_Defect_Summary.xlsx")
    overall, counts, executed = build_status_report(results, log["defects"], log["issues"], run_time, OUT / "OpsDesk_QA_Status_Report.html")
    print(f"Status {overall}: executed {executed}, pass {counts['Pass']}, fail {counts['Fail']}, blocked {counts['Blocked']}")
    print(f"Wrote {OUT / 'OpsDesk_Defect_Summary.xlsx'} and {OUT / 'OpsDesk_QA_Status_Report.html'}")


if __name__ == "__main__":
    main()
