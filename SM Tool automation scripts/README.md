# OpsDesk QA

The test design, RTM, automation, defect summary and QA status report for **OpsDesk**, the multi-tenant ITIL service desk.

## Layout

```
OpsDesk_Application_Documentation.docx   requirements baseline (build 28-Oct-2026)
deliverables/
  OpsDesk_Test_Design_RTM.xlsx            strategy, requirements, scenarios, 168 test cases, RTM, design-technique tables
  OpsDesk_Defect_Summary.xlsx             defect log, issues & blockers, automation failures to triage, summaries
  OpsDesk_QA_Status_Report.html           stakeholder status report (RAG, progress, defects, blockers, next steps)
  execution_results.json                  merged per-TC results (generated)
test-design/
  opsdesk_test_data.py                    SINGLE SOURCE of requirements + test cases (edit here, then rebuild)
  build_test_design.py                    builds the workbook
reporting/
  defect_log.json                         defect log + issue register (maintained by QA)
  manual_results.csv                      manual execution results (TC ID,Status,Actual Result,Defect ID,Executed By,Executed On)
  generate_reports.py                     merges results -> RTM, defect summary, status report
automation/                               Playwright + Cucumber BDD (TypeScript)
  features/        Gherkin features; every scenario tagged @TC-<MODULE>-<NNN> (maps to the workbook)
  fixture/         JSON test data: users.json, testdata.json, routes.json, files/
  modal/<area>/    <area>.data.ts (test data) · <area>.page.ts (actions) · <area>.modal.ts (locators)
  step/            step definitions
  support/         Cucumber World, hooks, config, {role}/{ticketType} parameter types
```

## Run the automation

```powershell
cd automation
npm install
npx playwright install chromium firefox
# .env holds OPSDESK_BASE_URL and OPSDESK_PASSWORD (copy from .env.example)
npm run test:smoke                     # @smoke scenarios
npm test                               # full suite (excludes @manual)
npm run test:tc "@TC-INC-003"          # one test case
npm run test:headed                    # watch it run
npm run test:firefox / test:edge       # cross-browser smoke (TC-NFR-005)
npm run qa-reports                     # rebuild RTM, defect summary and status report from reports/cucumber.json
```

Reports: `automation/reports/cucumber.html` and `cucumber.json`. In the HTML report:

- **Every Gherkin step has a ▶ screenshot link.** Click it to expand a capture of the page that step acted on, taken right after the step finished. Steps that only make HTTP requests (some NFR checks) have none.
- **A failed scenario also gets a full-page "failure screenshot"** of every open page, plus the URL at failure.
- Screenshots are embedded JPEGs, so the report is a single file you can share as-is. A dry run (`npm run dry-run`) never overwrites it.

### Tags

Each tag line starts with the functionality being tested, followed by the test case ID and control tags:

```gherkin
@authentication @FR-01                                   # feature: the functional area
  @logout @TC-AUTH-008 @smoke @security @readonly        # scenario: the functionality, then its TC id
```

| Tag kind | Examples | Used for |
|---|---|---|
| Functional area (feature) | `@authentication`, `@ticket_lifecycle`, `@report_export` | run a whole area |
| Functionality (scenario) | `@logout`, `@internal_note_privacy`, `@priority_matrix` | run one behaviour |
| Test case ID | `@TC-AUTH-008` | traceability to the RTM; **do not remove** |
| Category | `@smoke`, `@security`, `@FR-xx` | suites and requirement filtering |
| Control | `@readonly` (creates no data), `@customer`, `@teamlead`, `@superadmin` (skipped when that login is missing), `@manual` | execution control |

```powershell
npx cucumber-js --tags "@logout"
npx cucumber-js --tags "@ticket_lifecycle and not @customer"
```

Functional tags are defined in `test-design/opsdesk_test_data.py` (`FEATURE_TAGS`, `FUNCTION_TAGS`) and applied with `python test-design/apply_feature_tags.py`. That keeps the feature files and the workbook's "Automation Spec" column in sync.

- **Credentials:** emails are in `fixture/users.json`. The password comes from `.env` and is never committed. Scenarios tagged `@teamlead` or `@superadmin` skip automatically until those users have emails.
- **Test data:** tickets created by automation start with `QA-AUTO`, so you can find them and close them in bulk.

## First run against the live build: calibration

The UI wasn't reachable while this suite was being written (ngrok `ERR_NGROK_3200`), so the locators were written from the documentation, not the live UI. They use roles, labels and tolerant patterns, but expect to adjust some of them:

1. Run `npm run test:smoke` with `HEADLESS=false`.
2. Fix locators in `modal/<area>/<area>.modal.ts` and URLs in `fixture/routes.json`. Steps and features shouldn't need changes. `npm run codegen` helps you pick selectors.
3. Fill in `fixture/testdata.json → routing` (a category that routes to a team, and the employee's team) to enable TC-ASG-001 and TC-ASG-006.
4. Run the full suite, then triage the **Automation Failures** sheet: log real product defects in `reporting/defect_log.json`.

## Updating reports after manual testing

Add rows to `reporting/manual_results.csv` (Status: Pass / Fail / Blocked / N/A). Add any defects to `reporting/defect_log.json`, with the `tc` field linking each defect to its test case. Then run:

```powershell
python reporting/generate_reports.py --results automation/reports/cucumber.json
```

Manual results override automated ones for the same test case.
