@dashboard @FR-20 @FR-21 @readonly
Feature: Dashboard
  KPIs and charts with a 7/30/90-day period and account filter.
  Every figure respects the viewer's ticket visibility.

  @dashboard_kpi_cards @TC-DSH-001 @smoke
  Scenario: All KPI cards are displayed
    Given the manager is signed in
    When the manager opens the dashboard
    Then the manager sees the dashboard widgets:
      | Open now                |
      | Open and breached       |
      | At risk                 |
      | SLA met                 |
      | Avg first response      |
      | Mean time to resolve    |
      | CSAT                    |
      | AI suggestions accepted |

  @dashboard_period_filter @TC-DSH-002
  Scenario: The period can be switched between 7, 30 and 90 days
    Given the manager is signed in
    When the manager opens the dashboard
    And the manager selects each dashboard period
    Then the dashboard shows no errors

  @dashboard_account_filter @TC-DSH-003
  Scenario: The dashboard can be filtered by account
    Given the manager is signed in
    When the manager opens the dashboard
    And the manager filters the dashboard by an account
    Then the dashboard shows no errors

  @dashboard_common_charts @TC-DSH-004
  Scenario: Common charts are shown to every staff role
    Given the employee is signed in
    When the employee opens the dashboard
    Then the employee sees the dashboard widgets:
      | Created vs resolved |
      | Backlog age         |
      | Intake by channel   |
      | Open by priority    |

  @dashboard_lead_charts @TC-DSH-005
  Scenario: Lead-level charts are shown to the Manager
    Given the manager is signed in
    When the manager opens the dashboard
    Then the manager sees the dashboard widgets:
      | Accounts this period |
      | Open by team         |

  @dashboard_lead_charts_hidden @TC-DSH-006 @smoke @security @FR-02
  Scenario: Lead-level charts are hidden from the Employee
    Given the employee is signed in
    When the employee opens the dashboard
    Then the employee does not see the dashboard widgets:
      | Accounts this period |
      | Open by team         |
