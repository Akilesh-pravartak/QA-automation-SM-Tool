"""Build deliverables/OpsDesk_Test_Design_RTM.xlsx from opsdesk_test_data.py.

Usage:
    python build_test_design.py                       # design only (all cases "Not Run")
    python build_test_design.py --results ../deliverables/execution_results.json

The optional results file maps test case id -> {"status", "actual", "defect", "executed_by", "date"}
and is produced by reporting/generate_reports.py.
"""
import argparse
import json
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

import opsdesk_test_data as d

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "deliverables" / "OpsDesk_Test_Design_RTM.xlsx"

FONT = "Arial"
HDR_FILL = PatternFill("solid", fgColor="1F3864")
SUB_FILL = PatternFill("solid", fgColor="D9E1F2")
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
STATUSES = ["Not Run", "Pass", "Fail", "Blocked", "N/A"]


def style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
        cell.fill = HDR_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = BORDER


def write_table(ws, start_row, headers, rows, widths):
    for i, h in enumerate(headers, start=1):
        ws.cell(row=start_row, column=i, value=h)
    style_header(ws, start_row, len(headers))
    for r, row in enumerate(rows, start=start_row + 1):
        for c, v in enumerate(row, start=1):
            cell = ws.cell(row=r, column=c, value=v)
            if isinstance(v, str) and v.startswith("="):
                cell.data_type = "s"  # literal test data such as CSV-injection payloads, not a formula
            cell.font = Font(name=FONT, size=9)
            cell.alignment = WRAP
            cell.border = BORDER
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=start_row + 1, column=1)
    last = start_row + len(rows)
    ws.auto_filter.ref = f"A{start_row}:{get_column_letter(len(headers))}{max(last, start_row + 1)}"
    return last


def title(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = Font(name=FONT, bold=True, size=14, color="1F3864")
    if sub:
        ws["A2"] = sub
        ws["A2"].font = Font(name=FONT, italic=True, size=9, color="595959")


def strategy_sheet(wb):
    ws = wb.active
    ws.title = "Test Strategy"
    title(ws, "OpsDesk — Test Design & Requirements Traceability",
          f"Prepared {date.today():%d-%b-%Y} · Basis: OpsDesk_Application_Documentation.docx (build 28-Oct-2026) and project ticket-flow description")
    sections = [
        ("Objective", "Verify that OpsDesk meets its documented functional behaviour (ticket intake, priority, SLA, routing, workflows, closure, audit, dashboard, exports) and enforces role-based visibility and workspace isolation."),
        ("Application under test", "OpsDesk — multi-tenant ITIL service desk. URL: https://retiree-crying-manhandle.ngrok-free.dev/ (ngrok tunnel; URL changes if the tunnel is restarted)."),
        ("In scope", "Portal and staff web UI for Customer, Employee and Manager roles; ticket types INC/REQ/CHG; priority matrix; SLA timers and pauses; assignment; incident/request/change workflows; history/audit; dashboard; CSV/PDF exports; knowledge base; basic security and NFR checks."),
        ("Out of scope / limited", "Email, WhatsApp, monitoring and API intake (endpoints not supplied — manual cases only); Approvals and CMDB Explorer (switched off in the interface); multi-workspace isolation (needs a second workspace created via CLI); load testing."),
        ("Credentials & role coverage", "Customer: sakthibalaji.m · Employee: saraswathi.karunanidhi · Manager: sivasrigananapathi.sundaram (confirmed Manager; also listed as 'Admin'). No Team lead or Super admin login was supplied, so Team-lead-only and Administration cases are marked 'Automation blocked' until credentials are provided."),
        ("Test design techniques", "Equivalence partitioning (roles, ticket types, periods), boundary value analysis (priority bands, 75% at-risk threshold, 5-day auto-close, CSAT 1–5), decision tables (priority matrix, role × screen/action, SLA targets), state-transition testing (incident/request/change lifecycles), use-case testing (end-to-end ticket flow), error guessing (IDOR, XSS, CSV injection), data reconciliation (dashboard and exports)."),
        ("Automation approach", "Playwright + Cucumber BDD (TypeScript): Gherkin feature files, JSON fixtures, a modal layer per screen (data / page actions / locators) and step definitions; one browser context per role with saved sign-in state; every scenario is tagged with its TC id so results map back to this workbook and the RTM. Time-based (SLA alerts, auto-close), channel, AI and destructive admin cases stay manual."),
        ("Entry criteria", "Build deployed and tunnel reachable; test credentials valid; this design reviewed; test data (accounts/categories) known."),
        ("Exit criteria", "100% of High priority cases executed; no open Critical/High defects without an agreed workaround; ≥95% pass rate on executed High cases; RTM shows every requirement covered and executed (or formally deferred)."),
        ("Severity definitions", "Critical — data exposure, security breach or core flow unusable, no workaround. High — major function broken or wrong (e.g. SLA miscalculated). Medium — function partially wrong, workaround exists. Low — cosmetic or documentation issue."),
        ("Key risks", "1) Tunnel availability (ERR_NGROK_3200 observed 30-Oct-2026). 2) Shared test accounts — destructive cases must use throw-away users. 3) Time-dependent SLA behaviour needs clock control or long waits. 4) UI locators not yet calibrated against the live build. 5) Missing Team lead / Super admin credentials."),
    ]
    r = 4
    for k, v in sections:
        ws.cell(row=r, column=1, value=k).font = Font(name=FONT, bold=True, size=10)
        ws.cell(row=r, column=1).fill = SUB_FILL
        ws.cell(row=r, column=1).alignment = WRAP
        c = ws.cell(row=r, column=2, value=v)
        c.font = Font(name=FONT, size=10)
        c.alignment = WRAP
        ws.row_dimensions[r].height = max(30, 15 * (len(v) // 110 + 1))
        r += 1
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 120
    r += 1
    ws.cell(row=r, column=1, value="How to use").font = Font(name=FONT, bold=True, size=10)
    ws.cell(row=r, column=2, value=(
        "Execution columns on 'Test Cases' (yellow: Status, Actual Result, Defect ID, Executed By, Executed On) are the only cells to edit by hand. "
        "Status must be one of Not Run / Pass / Fail / Blocked / N/A. The RTM and Summary sheets recalculate from those columns. "
        "Automated runs fill them in via reporting/generate_reports.py.")).alignment = WRAP
    ws.cell(row=r, column=2).font = Font(name=FONT, size=10)
    ws.row_dimensions[r].height = 45


def requirements_sheet(wb):
    ws = wb.create_sheet("Requirements")
    title(ws, "Requirements Baseline")
    write_table(ws, 3, ["Req ID", "Title", "Description", "Source", "Priority"],
                d.REQUIREMENTS, [10, 28, 90, 28, 10])


def scenarios_sheet(wb):
    ws = wb.create_sheet("Test Scenarios")
    title(ws, "Test Scenarios", "Counts are formulas over the 'Test Cases' sheet.")
    rows = []
    for i, (code, (name, obj)) in enumerate(d.MODULES.items(), start=1):
        reqs = sorted({x.strip() for c in d.TEST_CASES if c["module"] == code for x in c["req"].split(",")},
                      key=lambda s: (s.startswith("NFR"), s))
        rows.append([f"TS-{i:02d}", code, name, obj, ", ".join(reqs), None, None, None, None])
    last = write_table(ws, 3, ["Scenario ID", "Module", "Scenario", "Objective", "Requirements",
                               "# Test Cases", "# Automated", "# Manual", "# Blocked"],
                       rows, [11, 9, 26, 60, 28, 11, 11, 10, 10])
    tcs = "'Test Cases'"
    for r in range(4, last + 1):
        ws[f"F{r}"] = f"=COUNTIF({tcs}!$C:$C,B{r})"
        ws[f"G{r}"] = f'=COUNTIFS({tcs}!$C:$C,B{r},{tcs}!$L:$L,"Automated")'
        ws[f"H{r}"] = f'=COUNTIFS({tcs}!$C:$C,B{r},{tcs}!$L:$L,"Manual")'
        ws[f"I{r}"] = f'=COUNTIFS({tcs}!$C:$C,B{r},{tcs}!$L:$L,"Automation blocked")'
    t = last + 1
    ws[f"E{t}"] = "Total"
    ws[f"E{t}"].font = Font(name=FONT, bold=True)
    for col in "FGHI":
        ws[f"{col}{t}"] = f"=SUM({col}4:{col}{last})"
        ws[f"{col}{t}"].font = Font(name=FONT, bold=True)


TC_HEADERS = ["TC ID", "Req ID(s)", "Module", "Title", "Role", "Preconditions", "Test Steps", "Test Data",
              "Expected Result", "Priority", "Type", "Automation", "Design Technique", "Automation Spec",
              "Notes", "Status", "Actual Result", "Defect ID", "Executed By", "Executed On"]


def test_cases_sheet(wb, results):
    ws = wb.create_sheet("Test Cases")
    title(ws, "Test Cases", "Yellow columns are execution inputs. Status: Not Run / Pass / Fail / Blocked / N/A.")
    rows = []
    for c in d.TEST_CASES:
        res = results.get(c["id"], {})
        status = res.get("status") or ("Blocked" if c["automation"] == d.BLOCKED else "Not Run")
        rows.append([c["id"], c["req"], c["module"], c["title"], c["role"], c["pre"], c["steps"], c["data"],
                     c["expected"], c["priority"], c["type"], c["automation"], c["technique"], c["spec"], c["note"],
                     status, res.get("actual", ""), res.get("defect", ""), res.get("executed_by", ""), res.get("date", "")])
    last = write_table(ws, 3, TC_HEADERS, rows,
                       [13, 12, 8, 36, 14, 28, 46, 18, 42, 9, 12, 14, 18, 24, 30, 10, 36, 11, 12, 12])
    for col in "PQRST":
        for r in range(4, last + 1):
            ws[f"{col}{r}"].fill = INPUT_FILL
    ws["U3"] = "Req Key"
    for r in range(4, last + 1):
        ws[f"U{r}"] = f'=", "&B{r}&","'
    ws.column_dimensions["U"].hidden = True
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"P4:P{last}")
    rng = f"P4:P{last}"
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Pass"'], fill=PatternFill("solid", fgColor="C6EFCE")))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Fail"'], fill=PatternFill("solid", fgColor="FFC7CE")))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Blocked"'], fill=PatternFill("solid", fgColor="F4B183")))
    ws.freeze_panes = "E4"


def rtm_sheet(wb):
    ws = wb.create_sheet("RTM")
    title(ws, "Requirements Traceability Matrix",
          "Forward traceability Requirement → Test Cases → Execution. Counts are formulas over 'Test Cases'; a case tracing to several requirements counts for each.")
    headers = ["Req ID", "Requirement", "Priority", "Source", "Test Case IDs", "# TCs", "# Automated", "# Manual",
               "# Auto-blocked", "Pass", "Fail", "Blocked", "Not Run", "Executed %", "Pass % (of executed)", "Coverage Status"]
    rows = []
    for rid, name, _desc, src, pri in d.REQUIREMENTS:
        ids = [c["id"] for c in d.TEST_CASES if rid in [x.strip() for x in c["req"].split(",")]]
        rows.append([rid, name, pri, src, ", ".join(ids)] + [None] * 11)
    last = write_table(ws, 3, headers, rows, [9, 26, 9, 24, 60, 7, 10, 9, 10, 7, 7, 8, 9, 10, 11, 22])
    tcs = "'Test Cases'"
    for r in range(4, last + 1):
        # match against the delimited key column so "FR-01" never matches "NFR-01"
        def cnt(extra=""):
            return f'COUNTIFS({tcs}!$U:$U,"*, "&A{r}&",*"{extra})'
        ws[f"F{r}"] = "=" + cnt()
        ws[f"G{r}"] = "=" + cnt(f',{tcs}!$L:$L,"Automated"')
        ws[f"H{r}"] = "=" + cnt(f',{tcs}!$L:$L,"Manual"')
        ws[f"I{r}"] = "=" + cnt(f',{tcs}!$L:$L,"Automation blocked"')
        ws[f"J{r}"] = "=" + cnt(f',{tcs}!$P:$P,"Pass"')
        ws[f"K{r}"] = "=" + cnt(f',{tcs}!$P:$P,"Fail"')
        ws[f"L{r}"] = "=" + cnt(f',{tcs}!$P:$P,"Blocked"')
        ws[f"M{r}"] = "=" + cnt(f',{tcs}!$P:$P,"Not Run"')
        ws[f"N{r}"] = f"=IF(F{r}=0,0,(J{r}+K{r})/F{r})"
        ws[f"O{r}"] = f"=IF(J{r}+K{r}=0,0,J{r}/(J{r}+K{r}))"
        ws[f"P{r}"] = (f'=IF(F{r}=0,"NOT COVERED",IF(K{r}>0,"Covered – FAILING",'
                       f'IF(J{r}=F{r},"Covered – PASSED",IF(J{r}+K{r}>0,"Covered – IN PROGRESS","Covered – NOT EXECUTED"))))')
        for col in "NO":
            ws[f"{col}{r}"].number_format = "0%"
        for col in "FGHIJKLMNOP":
            ws[f"{col}{r}"].font = Font(name=FONT, size=9)
            ws[f"{col}{r}"].border = BORDER
    rng = f"P4:P{last}"
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("FAILING",P4))'], fill=PatternFill("solid", fgColor="FFC7CE")))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("PASSED",P4))'], fill=PatternFill("solid", fgColor="C6EFCE")))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("NOT COVERED",P4))'], fill=PatternFill("solid", fgColor="FF0000")))
    ws.freeze_panes = "C4"


def technique_sheets(wb):
    ws = wb.create_sheet("Priority Decision Table")
    title(ws, "Priority Matrix — Decision Table (TC-PRI-001/002)", "Default matrix, Doc §6: P1 sum ≤3, P2 =4, P3 5–6, P4 7–8. Impact/urgency 1 = highest.")
    last = write_table(ws, 3, ["Impact", "Urgency", "Sum", "Expected Priority", "Boundary?"],
                       [[i, u, s, p, ""] for i, u, s, p in d.PRIORITY_DECISION_TABLE], [10, 10, 8, 16, 12])
    for r in range(4, last + 1):
        ws[f"C{r}"] = f"=A{r}+B{r}"
        ws[f"E{r}"] = f'=IF(OR(C{r}=3,C{r}=4,C{r}=5,C{r}=6,C{r}=7),"Yes","")'

    ws = wb.create_sheet("SLA Targets")
    title(ws, "SLA Targets — Decision Table (TC-SLA-001..003)", "Doc §6. Standard = Mon–Fri 09:00–18:00 business hours; Premium = 24×7.")
    write_table(ws, 3, ["Priority", "Standard Response", "Standard Resolution", "Premium Response", "Premium Resolution"],
                d.SLA_TARGETS, [10, 18, 18, 18, 18])
    r = 9
    for k, v in [("Pauses SLA", "Waiting on customer, Awaiting approval"),
                 ("Does not pause", "Waiting on third party"),
                 ("At-risk alert", "75% of SLA time (per-policy threshold) — BVA at 74% / 75% / 76%"),
                 ("First response", "First public staff reply (internal notes do not count)"),
                 ("No SLA", "Change tickets (default setup)")]:
        ws.cell(row=r, column=1, value=k).font = Font(name=FONT, bold=True, size=9)
        ws.cell(row=r, column=2, value=v).font = Font(name=FONT, size=9)
        r += 1

    ws = wb.create_sheet("State Transitions")
    title(ws, "Incident Lifecycle — State Transition Table", "Doc §5.1 and ticket-flow steps 6–10.")
    write_table(ws, 3, ["From State", "Event / Action", "To State", "Allowed Roles", "Guard / Side-effect", "Covered By"],
                d.INCIDENT_TRANSITIONS, [20, 20, 22, 26, 30, 18])

    ws = wb.create_sheet("Role Matrix")
    title(ws, "Role × Capability Decision Table", "Doc §2. Y = allowed, N = denied.")
    write_table(ws, 3, ["Capability", "Customer", "Employee", "Team lead", "Manager", "Super admin", "Covered By"],
                d.ROLE_MATRIX, [40, 11, 11, 11, 11, 12, 34])


def summary_sheet(wb):
    ws = wb.create_sheet("Summary", 1)
    title(ws, "Test Design Summary", "All figures are live formulas over 'Test Cases' and 'RTM'.")
    tcs = "'Test Cases'"
    lines = [
        ("Total requirements", "=COUNTA(RTM!A4:A200)"),
        ("Requirements covered", '=COUNTIF(RTM!F4:F200,">0")'),
        ("Requirement coverage %", "=IF(B4=0,0,B5/B4)"),
        ("Total test cases", f"=COUNTA({tcs}!A4:A1000)"),
        ("Automated", f'=COUNTIF({tcs}!L:L,"Automated")'),
        ("Manual", f'=COUNTIF({tcs}!L:L,"Manual")'),
        ("Automation blocked", f'=COUNTIF({tcs}!L:L,"Automation blocked")'),
        ("Automation coverage % (automated / total)", "=IF(B7=0,0,B8/B7)"),
        ("High priority cases", f'=COUNTIF({tcs}!J:J,"High")'),
        ("Medium priority cases", f'=COUNTIF({tcs}!J:J,"Medium")'),
        ("Low priority cases", f'=COUNTIF({tcs}!J:J,"Low")'),
        ("Executed (Pass + Fail)", f'=COUNTIF({tcs}!P:P,"Pass")+COUNTIF({tcs}!P:P,"Fail")'),
        ("Passed", f'=COUNTIF({tcs}!P:P,"Pass")'),
        ("Failed", f'=COUNTIF({tcs}!P:P,"Fail")'),
        ("Blocked", f'=COUNTIF({tcs}!P:P,"Blocked")'),
        ("Not run", f'=COUNTIF({tcs}!P:P,"Not Run")'),
        ("Execution progress %", "=IF(B7=0,0,B15/B7)"),
        ("Pass rate % (of executed)", "=IF(B15=0,0,B16/B15)"),
    ]
    for i, (k, f) in enumerate(lines, start=4):
        ws.cell(row=i, column=1, value=k).font = Font(name=FONT, size=10)
        c = ws.cell(row=i, column=2, value=f)
        c.font = Font(name=FONT, size=10, bold=True)
        if "%" in k:
            c.number_format = "0.0%"
    ws.column_dimensions["A"].width = 42
    ws.column_dimensions["B"].width = 14

    ws["D3"] = "By Type"
    ws["D3"].font = Font(name=FONT, bold=True)
    types = sorted({c["type"] for c in d.TEST_CASES})
    for i, t in enumerate(types, start=4):
        ws.cell(row=i, column=4, value=t).font = Font(name=FONT, size=10)
        ws.cell(row=i, column=5, value=f'=COUNTIF({tcs}!K:K,D{i})').font = Font(name=FONT, size=10, bold=True)
    ws.column_dimensions["D"].width = 18


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", help="execution_results.json produced by reporting/generate_reports.py")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    results = json.loads(Path(args.results).read_text(encoding="utf-8")) if args.results else {}

    wb = Workbook()
    strategy_sheet(wb)
    requirements_sheet(wb)
    scenarios_sheet(wb)
    test_cases_sheet(wb, results)
    rtm_sheet(wb)
    technique_sheets(wb)
    summary_sheet(wb)
    wb.calculation.fullCalcOnLoad = True
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    wb.save(args.out)
    print(f"Wrote {args.out} ({len(d.TEST_CASES)} test cases, {len(d.REQUIREMENTS)} requirements)")


if __name__ == "__main__":
    main()
