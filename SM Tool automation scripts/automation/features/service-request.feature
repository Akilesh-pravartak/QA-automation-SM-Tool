@service_request_lifecycle @FR-16
Feature: Service request lifecycle
  New -> (Awaiting approval) -> In fulfilment -> Fulfilled -> Closed.
  Approval scenarios are tagged @manual because Approvals are switched off in the current build.

  Background:
    Given a new service request raised by the manager and assigned to the employee

  @fulfil_without_approval @TC-REQ-001 @smoke
  Scenario: A request can go straight to fulfilment without approval
    When the employee performs "Start fulfilment"
    Then the ticket status is "In fulfilment"

  @fulfil_validation @TC-REQ-002
  Scenario: Fulfilling without resolution notes is blocked
    When the employee performs "Start fulfilment"
    And the employee tries to perform "Fulfil" without the required details
    Then the action is blocked and the status is unchanged

  @fulfil_and_close_request @TC-REQ-003 @smoke @FR-14 @customer
  Scenario: Fulfil with notes and the customer closes the request
    When the employee performs "Start fulfilment"
    And the employee fulfils the request with resolution notes
    Then the ticket status is "Fulfilled"
    When the customer performs "Confirm close"
    Then the ticket status is "Closed"

  @reopen_request @TC-REQ-004 @FR-14 @customer
  Scenario: Customer reopens a fulfilled request
    When the employee performs "Start fulfilment"
    And the employee fulfils the request with resolution notes
    And the customer performs "Reopen"
    Then the employee sees the ticket status "In fulfilment|In progress|Reopened|New"

  @reject_request @TC-REQ-005 @manual
  Scenario: Lead or manager rejects a request at the approval stage with a comment
    # Blocked: Approvals screens are switched off in the interface (Doc §4)
    When the manager performs "Reject"
    Then the ticket status is "Rejected"
