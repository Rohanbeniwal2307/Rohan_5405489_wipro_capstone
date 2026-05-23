Feature: 99acres New Launch end-to-end flow

  @regression @e2e
  Scenario: Apply New Launch filters and open View Number popup
    Given the user is on the 99acres homepage
    And manual login is completed when enabled for end to end flow
    When the user opens the New Launch module
    Then the New Launch search box should be visible
    When the user selects the configured location
    Then the configured location should be selected
    When the user submits the New Launch search
    Then New Launch results should be displayed for the configured location
    When the user applies the Residential Property Type filter
    Then the "Flat/Apartment" filter should be applied
    When the user applies the configured budget range filter
    Then search results should remain loaded
    When the user applies the configured bedroom filter
    Then the configured bedroom filter should be applied
    When the user opens the first building from the result list
    Then the project detail page should be opened
    When the user closes the project disclaimer if it is visible
    And the user clicks the View Number button
    Then the contact details or contact form should be visible
