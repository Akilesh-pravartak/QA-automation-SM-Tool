@history_and_audit @FR-19
Feature: History and audit
  Every change is recorded in the ticket history and in an append-only audit log.

  @ticket_history @TC-AUD-001
  Scenario: Ticket history shows each change with user and time
    Given a new incident raised by the manager
    When the manager assigns the ticket to the employee
    Then the manager sees a history entry with user and time

  @audit_log_search @TC-AUD-002 @superadmin
  Scenario: Super admin searches the audit log
    Given the super admin is signed in
    And a new incident raised by the manager
    When the manager assigns the ticket to the employee
    And the super admin searches the audit log for the ticket
    Then matching audit entries are listed

  @audit_log_tamper_proof @TC-AUD-003 @superadmin @security
  Scenario: Audit entries cannot be edited or deleted
    Given the super admin is signed in
    And a new incident raised by the manager
    When the super admin searches the audit log for the ticket
    Then the audit entries offer no edit or delete controls

  @audit_log_access @TC-AUD-005 @security @FR-02 @readonly
  Scenario: Employee cannot open the audit log
    Given the employee is signed in
    Then the employee is denied access to the "Audit log" page
