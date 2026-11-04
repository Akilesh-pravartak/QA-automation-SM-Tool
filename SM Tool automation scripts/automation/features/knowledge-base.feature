@knowledge_base @FR-24
Feature: Knowledge base

  @kb_read_and_vote @TC-KB-001 @customer
  Scenario: Customer reads and votes on a public article
    Given the customer is signed in
    When the customer opens the first published article
    Then the article content is readable
    When the customer votes the article helpful
    Then the vote is recorded

  @kb_article_management @TC-KB-003
  Scenario: Staff create, edit and delete an article
    Given the employee is signed in
    When the employee creates, edits and deletes a knowledge article
    Then the article no longer exists
