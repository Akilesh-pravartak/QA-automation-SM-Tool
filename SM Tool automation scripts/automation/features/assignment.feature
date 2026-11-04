@routing_and_assignment @FR-08 @FR-09
Feature: Routing and assignment
  Tickets are routed to a team; unassigned tickets are assigned by a Team lead or Manager.

  @auto_routing_by_category @TC-ASG-001
  Scenario: A ticket in a mapped category is routed to its team
    Given a category that routes to a team is configured
    And the employee is signed in
    When the employee raises a new incident in the routed category
    Then the manager sees the ticket routed to that team

  @unassigned_queue_routing @TC-ASG-002 @smoke
  Scenario: A ticket with no matching team lands in the unassigned queue
    Given a new unassigned incident raised by the manager
    Then the ticket is listed in the manager's unassigned queue
    And the employee cannot see the ticket in the list

  @assignee_filtered_by_team @TC-ASG-006
  Scenario: The assignee list is filtered by the selected team
    Given a new incident raised by the manager
    Then the assignee list offers the employee once the employee's team is selected

  @manual_assignment @TC-ASG-007 @smoke
  Scenario: Manager assigns an unassigned ticket and the employee can then see it
    Given a new incident raised by the manager
    When the manager assigns the ticket to the employee
    Then the employee can see the ticket

  @assignment_history @TC-ASG-008 @FR-19
  Scenario: Assignment is recorded in the ticket history
    Given a new incident raised by the manager
    When the manager assigns the ticket to the employee
    Then the ticket history shows the assignment
