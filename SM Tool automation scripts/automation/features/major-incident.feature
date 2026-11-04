@major_incident @FR-29
Feature: Major incidents
  Team leads and managers declare and coordinate major incidents.

  @declare_major_incident @TC-MI-001
  Scenario: Manager declares a major incident
    Given a new incident raised by the manager
    When the manager performs "Declare major incident"
    Then the ticket is flagged as a major incident

  @major_incident_permission @TC-MI-002 @security @FR-02
  Scenario: Employee cannot declare a major incident
    Given a new incident raised by the manager and assigned to the employee
    Then the employee does not have the "Declare major incident" action
