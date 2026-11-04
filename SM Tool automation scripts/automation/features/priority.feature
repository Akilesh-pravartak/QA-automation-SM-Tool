@priority_calculation @FR-06
Feature: Priority calculation from impact and urgency
  Default matrix (Doc §6): P1 when impact + urgency <= 3, P2 when 4, P3 when 5-6, P4 when 7-8

  Background:
    Given a new incident raised by the manager
    And the manager is signed in

  @priority_matrix @TC-PRI-001
  Scenario Outline: Priority decision table - impact <impact>, urgency <urgency>
    When the manager sets impact <impact> and urgency <urgency>
    Then the ticket priority is "<priority>"

    Examples:
      | impact | urgency | priority |
      | 1      | 1       | P1       |
      | 1      | 2       | P1       |
      | 1      | 3       | P2       |
      | 1      | 4       | P3       |
      | 2      | 1       | P1       |
      | 2      | 2       | P2       |
      | 2      | 3       | P3       |
      | 2      | 4       | P3       |
      | 3      | 1       | P2       |
      | 3      | 2       | P3       |
      | 3      | 3       | P3       |
      | 3      | 4       | P4       |
      | 4      | 1       | P3       |
      | 4      | 2       | P3       |
      | 4      | 3       | P4       |
      | 4      | 4       | P4       |

  @priority_boundaries @TC-PRI-002
  Scenario Outline: Priority band boundaries - sum <sum>
    When the manager sets impact <impact> and urgency <urgency>
    Then the ticket priority is "<priority>"

    Examples:
      | sum | impact | urgency | priority |
      | 3   | 1      | 2       | P1       |
      | 4   | 2      | 2       | P2       |
      | 5   | 2      | 3       | P3       |
      | 6   | 3      | 3       | P3       |
      | 7   | 3      | 4       | P4       |

  @priority_override @TC-PRI-003 @FR-07
  Scenario: Overriding priority recalculates the SLA due dates
    When the manager sets impact 4 and urgency 4
    And the manager records the SLA due dates
    And the manager changes the "priority" field to "P1"
    Then the SLA due dates are recalculated
    And the ticket history records the "priority" change

  @customer_priority_restriction @TC-PRI-004 @security @customer
  Scenario: Customer cannot set the priority
    Then the customer cannot edit the fields:
      | priority |
