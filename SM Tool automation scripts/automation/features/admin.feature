@administration @FR-25 @superadmin
Feature: Administration console (Super admin only)
  Skipped automatically until a Super admin credential is added to fixture/users.json.

  @user_admin_no_create @TC-ADM-001
  Scenario: The Users screen has no create or invite option
    Given the super admin is signed in
    Then the Users screen has no create or invite option

  @admin_pages_load @TC-ADM-011
  Scenario: Every Administration page loads
    Given the super admin is signed in
    When the super admin opens each Administration section:
      | Users          |
      | Teams          |
      | SLA policies   |
      | Business hours |
      | Configuration  |
      | Inbound outbox |
      | Audit log      |
