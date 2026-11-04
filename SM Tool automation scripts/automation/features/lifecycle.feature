@ticket_lifecycle
Feature: Ticket lifecycle - support work, waiting states, resolution and closure
  Ticket flow steps 6-10: Employee works the ticket, waits on the customer,
  resolves it, and the customer confirms closure or reopens.

  Background:
    Given a new incident raised by the manager and assigned to the employee

  # ---------------- support work (FR-10) ----------------

  @public_reply @TC-WRK-001 @smoke @FR-10 @customer
  Scenario: A public reply is visible to the customer
    When the employee sends a public reply
    Then the customer sees the public reply

  @internal_note_privacy @TC-WRK-002 @smoke @security @FR-10 @customer
  Scenario: An internal note is hidden from the customer
    When the employee adds an internal note
    Then the customer does not see the internal note

  @file_attachment @TC-WRK-003 @FR-10
  Scenario: Staff attach a file to a ticket
    When the employee attaches the sample file
    Then the attachment is listed on the ticket

  @ticket_field_edit @TC-WRK-004 @FR-10 @FR-19
  Scenario: Staff edit ticket fields and the history records it
    When the employee changes the "impact" field to "2"
    Then the ticket history records the "impact" change

  @customer_edit_subject @TC-WRK-005 @FR-23 @customer
  Scenario: Customer edits the subject of their own ticket
    When the customer edits the subject
    Then the new subject is saved

  @customer_field_restriction @TC-WRK-006 @security @FR-23 @customer
  Scenario: Customer cannot edit staff-only fields
    Then the customer cannot edit the fields:
      | assignee |
      | team     |
      | priority |
      | status   |

  # ---------------- incident workflow (FR-13, FR-14, FR-15) ----------------

  @start_work @TC-INC-001 @smoke @FR-15
  Scenario: Start work moves the incident to In progress
    When the employee performs "Start work"
    Then the ticket status is "In progress"

  @resolve_validation @TC-INC-002 @FR-13
  Scenario: Resolving without a resolution code and notes is blocked
    When the employee performs "Start work"
    And the employee tries to perform "Resolve" without the required details
    Then the action is blocked and the status is unchanged

  @resolve_incident @TC-INC-003 @smoke @FR-13
  Scenario: Resolving with a resolution code and notes
    When the employee performs "Start work"
    And the employee resolves the ticket with a resolution code and notes
    Then the ticket status is "Resolved"

  @resolve_from_new @TC-INC-004 @FR-15
  Scenario: An incident can be resolved directly from New
    When the manager resolves the ticket with a resolution code and notes
    Then the ticket status is "Resolved"

  @confirm_closure @TC-INC-005 @smoke @FR-14 @customer
  Scenario: Customer confirms closure of a resolved incident
    When the employee resolves the ticket with a resolution code and notes
    And the customer performs "Confirm close"
    Then the ticket status is "Closed"

  @reopen_incident @TC-INC-006 @FR-14 @customer
  Scenario: Customer reopens a resolved incident
    When the employee resolves the ticket with a resolution code and notes
    And the customer performs "Reopen"
    Then the employee sees the ticket status "In progress|Reopened|New"

  @cancel_with_comment @TC-INC-007 @FR-15
  Scenario: Cancelling requires a comment
    When the employee tries to perform "Cancel" without the required details
    Then the action is blocked and the status is unchanged
    When the employee performs "Cancel"
    Then the ticket status is "Cancelled"

  @customer_cannot_cancel @TC-INC-008 @security @FR-15 @customer
  Scenario: Customer cannot cancel a ticket
    Then the customer does not have the "Cancel" action

  @closed_ticket_transitions @TC-INC-009 @FR-15 @customer
  Scenario: A closed ticket offers no further work transitions
    When the employee resolves the ticket with a resolution code and notes
    And the customer performs "Confirm close"
    Then the manager does not have the "Start work" action
    And the manager does not have the "Resolve" action

  # ---------------- waiting states (FR-11) ----------------

  @waiting_on_customer_sla_pause @TC-WAIT-001 @smoke @FR-11
  Scenario: Waiting on customer pauses the SLA
    When the employee performs "Start work"
    And the employee performs "Ask customer"
    Then the ticket status is "Waiting on customer"
    And the SLA is shown as paused

  @customer_reply_resumes_work @TC-WAIT-002 @smoke @FR-11 @customer
  Scenario: A customer reply returns the ticket to work
    When the employee performs "Start work"
    And the employee performs "Ask customer"
    And the customer sends a public reply
    Then the employee sees the ticket status "In progress"

  @waiting_on_third_party @TC-WAIT-003 @FR-11
  Scenario: Waiting on third party does not pause the SLA
    When the employee performs "Start work"
    And the employee performs "Wait on third party"
    Then the ticket status is "Waiting on third party"
    And the SLA is not shown as paused
