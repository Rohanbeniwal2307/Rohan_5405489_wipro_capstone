Feature: 99acres New Launch positive and negative checks

  @smoke @positive
  Scenario: Open the New Launch module successfully from the homepage
    Given the user is on the 99acres homepage
    When the user opens the New Launch module
    Then the New Launch search box should be visible
    And the New Launch search box should be empty

  @smoke @positive
  Scenario: Search for a valid location in the New Launch module
    Given the user is on the 99acres homepage
    When the user opens the New Launch module
    And the user searches for the configured valid location
    Then New Launch results should be displayed for the configured location

  @smoke @positive
  Scenario: Display location suggestions for a valid partial location
    Given the user is on the 99acres homepage
    When the user opens the New Launch module
    And the user enters partial location "Noi"
    Then location suggestions should be displayed
    And the suggestions should include "Noida"

  @smoke @positive
  Scenario: Apply the Residential Property Type filter on search results
    Given the user is on the 99acres homepage
    When the user opens the New Launch module
    And the user searches for the configured valid location
    And the user applies the Residential Property Type filter
    Then the "Flat/Apartment" filter should be applied
    And search results should remain loaded

  @regression @negative
  Scenario: Invalid location should not show valid suggestions or proceed
    Given the user is on the 99acres homepage
    When the user opens the New Launch module
    And the user enters invalid location "xyzabc123"
    Then the invalid location should remain in the search box
    And valid location suggestions should not be displayed
    And the application should not navigate away from the New Launch search

  @regression @negative
  Scenario: Search should not proceed without entering a location
    Given the user is on the 99acres homepage
    When the user opens the New Launch module
    And the user clicks Search without entering a location
    Then the application should not navigate away from the New Launch search
    And the New Launch search box should be visible
    And the New Launch search box should be empty
