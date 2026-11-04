@ticket_creation @FR-04 @FR-05
Feature: Ticket creation and numbering
  Customers raise Incidents and Service Requests; Changes are staff-only.
  Every ticket gets a gap-free number with its type prefix (INC-000001 format).
  The new-ticket form is shared by all roles, so form-field checks run as staff
  until a customer login is available.

  @raise_incident @TC-TKT-001 @smoke @customer
  Scenario: Customer raises an Incident from the portal
    Given the customer is signed in
    When the customer raises a new incident
    Then the ticket number starts with "INC"
    And the customer sees the ticket status "New"
    And the customer sees the ticket came via "Portal"

  @raise_service_request @TC-TKT-002 @smoke @customer
  Scenario: Customer raises a Service Request from the portal
    Given the customer is signed in
    When the customer raises a new service request
    Then the ticket number starts with "REQ"
    And the customer sees the ticket status "New"

  @customer_ticket_types @TC-TKT-003 @smoke @readonly @customer
  Scenario: Customer can choose only Incident and Service Request
    Given the customer is signed in
    When the customer opens the new ticket form
    Then the ticket types offered to the customer are:
      | type     | offered |
      | incident | yes     |
      | request  | yes     |
      | change   | no      |
      | problem  | no      |

  @incident_form_fields @TC-TKT-004 @readonly
  Scenario: Incident form asks for Environment and Error message
    Given the employee is signed in
    When the employee opens the new ticket form for an incident
    Then the employee sees the form fields:
      | environment   |
      | error message |

  @service_request_form_fields @TC-TKT-005 @readonly
  Scenario: Service Request form asks for Requested for and Needed by
    Given the employee is signed in
    When the employee opens the new ticket form for a service request
    Then the employee sees the form fields:
      | requested for |
      | needed by     |

  @raise_change @TC-TKT-006
  Scenario: Staff raise a Change with change-specific fields
    Given the manager is signed in
    When the manager opens the new ticket form for a change
    Then the manager sees the form fields:
      | change type           |
      | risk                  |
      | implementation window |
      | back-?out plan        |
      | outcome               |
    When the manager raises a new change
    Then the ticket number starts with "CHG"
    And the manager sees the ticket status "Draft"

  @mandatory_field_validation @TC-TKT-007 @readonly
  Scenario: Mandatory fields are validated
    Given the employee is signed in
    When the employee opens the new ticket form for an incident
    And the employee submits the form with an empty subject and description
    Then the employee sees a validation message and the form is not submitted

  @kb_suggestions_while_typing @TC-TKT-010 @FR-24 @readonly
  Scenario: Knowledge articles and past fixes are suggested while typing
    Given the employee is signed in
    When the employee opens the new ticket form for an incident
    And the employee types the knowledge search term into the subject
    Then the employee sees knowledge-base suggestions

  @xss_protection @TC-TKT-011 @smoke @security @NFR-01
  Scenario: A script in the subject is shown as text (XSS)
    Given the employee is signed in
    When the employee raises a new incident whose subject contains a script payload
    Then the payload is displayed as text and no script runs for the employee
    And the payload is displayed as text and no script runs for the manager

  @ticket_numbering @TC-TKT-012
  Scenario: Ticket numbers are sequential
    Given the manager is signed in
    When the manager raises 3 incidents in a row
    Then the ticket numbers are strictly increasing
