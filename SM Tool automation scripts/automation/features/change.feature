@change_lifecycle @FR-17
Feature: Change lifecycle
  Draft -> Assessment -> CAB review -> Scheduled -> Implementing -> PIR -> Closed.
  Required details gate each stage; rejection and closure are lead/manager actions.

  @change_form_access @TC-CHG-001 @security @FR-04 @customer
  Scenario: Customer cannot open the change form directly
    Given the customer is signed in
    Then the customer is denied access to the "New change form" page

  @change_assessment_gate @TC-CHG-002
  Scenario: Submitting for assessment needs change type, risk and back-out plan
    Given a new change raised by the manager
    When the manager tries to perform "Submit for assessment" without the required details
    Then the action is blocked and the status is unchanged
    When the manager fills the change fields:
      | Change type   |
      | Risk          |
      | Back-out plan |
    And the manager performs "Submit for assessment"
    Then the ticket status is "Assessment"

  @change_cab_gate @TC-CHG-003
  Scenario: Sending to CAB needs an implementation window
    Given a new change raised by the manager
    When the manager fills the change fields:
      | Change type   |
      | Risk          |
      | Back-out plan |
    And the manager performs "Submit for assessment"
    And the manager tries to perform "Send to CAB" without the required details
    Then the action is blocked and the status is unchanged
    When the manager fills the change fields:
      | Implementation window |
    And the manager performs "Send to CAB"
    Then the ticket status is "CAB review|Change-board"

  @change_reject_close_permission @TC-CHG-006 @security @FR-02
  Scenario: Employee cannot reject or close a change
    Given a new change raised by the manager and assigned to the employee
    Then the employee does not have the "Reject" action
    And the employee does not have the "Close" action
