@sla_timers @FR-07
Feature: SLA timers
  Time-based SLA targets, business hours and alerts are verified manually (see the test design workbook).

  @change_has_no_sla @TC-SLA-005
  Scenario: Change tickets have no SLA timer
    Given a new change raised by the manager
    Then the ticket has no SLA timer

  @first_response_sla @TC-SLA-008 @FR-10
  Scenario: Only a public staff reply counts as the first response
    Given a new incident raised by the manager and assigned to the employee
    When the employee adds an internal note
    Then the response SLA is "not met"
    When the employee sends a public reply
    Then the response SLA is "met"
