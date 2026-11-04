@role_based_access @FR-02
Feature: Role-based access control
  Each role sees only the screens, tickets and actions it is allowed to (Doc §2)

  @customer_dashboard_access @TC-RBAC-001 @smoke @security @readonly @customer
  Scenario: Customer cannot open the Dashboard
    Given the customer is signed in
    Then the customer does not see the "Dashboard" menu
    And the customer is denied access to the "Dashboard" page

  @customer_admin_access @TC-RBAC-002 @security @readonly @customer
  Scenario: Customer cannot open Administration
    Given the customer is signed in
    Then the customer is denied access to the "Administration" page

  @employee_admin_access @TC-RBAC-003 @smoke @security @readonly
  Scenario: Employee cannot open Administration
    Given the employee is signed in
    Then the employee does not see the "Administration" menu
    And the employee is denied access to the "Administration" page

  @manager_admin_access @TC-RBAC-012 @security @readonly
  Scenario: Manager cannot open Administration
    Given the manager is signed in
    Then the manager does not see the "Administration" menu
    And the manager is denied access to the "Administration" page

  @employee_ticket_visibility @TC-RBAC-004 @smoke @security @FR-09
  Scenario: Employee sees only their own tickets and no unassigned tickets
    Given a new unassigned incident raised by the manager
    And the employee is signed in
    Then the employee's unassigned queue lists no tickets
    And every ticket in the employee's open list is assigned to the employee
    And the employee cannot see the ticket in the list

  @team_lead_ticket_visibility @TC-RBAC-005 @teamlead @security @readonly
  Scenario: Team lead sees all tickets but not Administration
    Given the team lead is signed in
    Then the team lead sees the same open tickets as the manager
    And the team lead does not see the "Administration" menu
    And the team lead is denied access to the "Administration" page

  @manager_unassigned_visibility @TC-RBAC-006 @FR-09
  Scenario: Manager sees unassigned tickets
    Given a new unassigned incident raised by the manager
    Then the ticket is listed in the manager's unassigned queue

  @super_admin_console_access @TC-RBAC-007 @superadmin @readonly
  Scenario: Super admin opens every Administration section
    Given the super admin is signed in
    When the super admin opens each Administration section:
      | Users          |
      | Teams          |
      | SLA policies   |
      | Business hours |
      | Configuration  |
      | Inbound outbox |
      | Audit log      |

  @customer_ticket_url_tampering @TC-RBAC-008 @smoke @security @NFR-01 @customer
  Scenario: Customer cannot open another account's ticket by URL (IDOR)
    Given the customer is signed in
    And a new incident raised by the manager
    Then the customer cannot open the ticket by its URL

  @employee_ticket_url_tampering @TC-RBAC-009 @security @NFR-01
  Scenario: Employee cannot open an unassigned ticket by URL (IDOR)
    Given a new unassigned incident raised by the manager
    And the employee is signed in
    Then the employee cannot open the ticket by its URL

  @super_admin_account_protection @TC-RBAC-010 @superadmin @FR-25 @readonly
  Scenario: The Super admin account cannot be edited, deactivated or reset
    Given the super admin is signed in
    Then the super admin account row has no edit, deactivate or reset actions
