@customer_portal @FR-23
Feature: Customer self-service portal

  @customer_portal_reply @TC-CUS-002 @smoke @customer
  Scenario: Customer replies from the portal and staff see it
    Given a new incident raised by the customer and assigned to the employee
    When the customer sends a public reply
    Then the employee sees the public reply

  @pwa_install @TC-CUS-003 @customer
  Scenario: The portal can be installed as a web app
    Given the customer is signed in
    Then the portal exposes a valid web app manifest

  @mobile_layout @TC-CUS-004 @NFR-02 @customer
  Scenario: The new request form works on a phone-sized screen
    Given the customer is signed in
    When the customer uses a mobile viewport
    Then the new request form fits the screen without horizontal scrolling

  @customer_no_internal_note @TC-CUS-005 @security @customer
  Scenario: Customer has no internal note option
    Given a new incident raised by the customer
    Then the customer cannot write an internal note
