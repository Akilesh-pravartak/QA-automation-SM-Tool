@non_functional @readonly
Feature: Non-functional checks - security and performance basics

  @https_enforced @TC-NFR-001 @security @NFR-01
  Scenario: The application is served over HTTPS only
    Then the plain HTTP address redirects to HTTPS

  @session_token_security @TC-NFR-002 @security @NFR-01 @readonly
  Scenario: The session token is not readable by page scripts
    Given the employee is signed in
    Then the employee session cookie is Secure and HttpOnly

  @security_headers @TC-NFR-003 @security @NFR-01
  Scenario: Security response headers are present
    Then the home page response includes security headers

  @page_load_performance @TC-NFR-004 @NFR-02
  Scenario Outline: The <page> page loads within the budget
    Given the manager is signed in
    When the manager loads the "<page>" page
    Then the page loads within the performance budget

    Examples:
      | page      |
      | Dashboard |
      | Tickets   |
