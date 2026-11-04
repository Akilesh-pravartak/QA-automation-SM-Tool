@authentication @FR-01
Feature: Authentication and session
  As an OpsDesk user
  I want to sign in and out securely
  So that only authorised people reach the service desk

  @customer_login @TC-AUTH-001 @smoke @readonly @customer
  Scenario: Customer signs in with valid credentials
    Given I am on the sign-in page
    When I sign in as the customer
    Then I land on the customer portal
    And the customer does not see the "Dashboard" menu
    And the customer does not see the "Administration" menu

  @employee_login @TC-AUTH-002 @smoke @readonly
  Scenario: Employee signs in with valid credentials
    Given I am on the sign-in page
    When I sign in as the employee
    Then I land on the dashboard
    And the signed-in user is shown with the role "employee"

  @manager_login @TC-AUTH-003 @smoke @readonly
  Scenario: Manager signs in and has no Administration entry
    Given I am on the sign-in page
    When I sign in as the manager
    Then I land on the dashboard
    And the signed-in user is shown with the role "manager"
    And the manager does not see the "Administration" menu

  @invalid_password_login @TC-AUTH-004 @smoke @readonly
  Scenario: Sign-in is rejected with a wrong password
    Given I am on the sign-in page
    When I sign in with the employee email and a wrong password
    Then a sign-in error is shown and I remain on the sign-in page

  @user_enumeration_check @TC-AUTH-005 @security @readonly
  Scenario: Unregistered email gives the same generic error (no user enumeration)
    Given I am on the sign-in page
    When I sign in with the employee email and a wrong password
    And I sign in with an unregistered email
    Then the error message is the same as for a wrong password

  @login_form_validation @TC-AUTH-006 @readonly
  Scenario Outline: Sign-in form validation for empty or malformed input
    When I submit the sign-in form with email "<email>" and password "<password>"
    Then sign-in validation is shown

    Examples:
      | email | password |
      |       |          |
      | abc@  |          |
      | abc@  | x        |

  @logout @TC-AUTH-008 @smoke @security @readonly
  Scenario: Sign-out ends the session
    Given the employee is signed in
    When the employee signs out
    Then the employee cannot return to a protected page using Back or reload

  @protected_page_redirect @TC-AUTH-009 @security @readonly
  Scenario Outline: Protected pages require sign-in
    Then opening the "<page>" page without signing in shows the sign-in page

    Examples:
      | page      |
      | Dashboard |
      | Tickets   |

  @email_case_insensitive_login @TC-AUTH-011 @readonly
  Scenario: Email is case-insensitive and the password is masked
    Given I am on the sign-in page
    Then the password field is masked
    When I sign in as the employee with the email in upper case
    Then I land on the dashboard
