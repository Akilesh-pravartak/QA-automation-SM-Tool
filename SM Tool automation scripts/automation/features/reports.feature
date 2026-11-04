@report_export @FR-22
Feature: Report exports
  Overview, Tickets, Major Incidents and Team Workload export as CSV or PDF,
  following the viewer's ticket visibility.

  @export_report_csv_pdf @readonly
  Scenario Outline: Export the <report> report as <format>
    Given the manager is signed in
    When the manager exports the "<report>" report as "<format>"
    Then a valid non-empty "<format>" file is downloaded

    @export_overview_report @TC-RPT-001 @smoke
    Examples: Overview
      | report   | format |
      | Overview | CSV    |
      | Overview | PDF    |

    @export_tickets_report @TC-RPT-002 @smoke
    Examples: Tickets
      | report  | format |
      | Tickets | CSV    |
      | Tickets | PDF    |

    @export_major_incidents_report @TC-RPT-003
    Examples: Major Incidents
      | report          | format |
      | Major Incidents | CSV    |
      | Major Incidents | PDF    |

    @export_team_workload_report @TC-RPT-004
    Examples: Team Workload
      | report        | format |
      | Team Workload | CSV    |
      | Team Workload | PDF    |

  @export_visibility @TC-RPT-005 @security @FR-02
  Scenario: An Employee's export excludes tickets they cannot see
    Given a new unassigned incident raised by the manager
    And the employee is signed in
    When the employee exports the "Tickets" report as "CSV"
    Then the export does not contain the ticket
