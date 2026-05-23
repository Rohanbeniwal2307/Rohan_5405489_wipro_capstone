from behave import given, then, when

from config.config_reader import ConfigReader
from pages.login_page import LoginPage
from pages.newlaunch_page import NewLaunchPage
from pages.property_details_page import PropertyDetailsPage
from utilities.logger import Logger
from utilities.screenshot import take_screenshot


def _page(context):
    if context.page is None:
        context.page = NewLaunchPage(context.driver)
    return context.page


@given("the user is on the 99acres homepage")
def step_user_is_on_homepage(context):
    context.logger = Logger.get_logger()
    context.logger.info("BDD scenario started")
    assert ConfigReader.get("application", "base_url") in context.driver.current_url


@given("manual login is completed when enabled for end to end flow")
def step_manual_login_when_enabled(context):
    if ConfigReader.getboolean("end_to_end", "login_enabled", fallback=False):
        take_screenshot(context.driver, "bdd_e2e_login_home_before_popup")
        LoginPage(context.driver).login_manually_and_return_home()
        take_screenshot(context.driver, "bdd_e2e_login_completed_home")
        assert ConfigReader.get("application", "base_url") in context.driver.current_url


@when("the user opens the New Launch module")
def step_open_new_launch_module(context):
    _page(context).open_new_launch_tab()
    take_screenshot(context.driver, "bdd_new_launch_opened")


@then("the New Launch search box should be visible")
def step_new_launch_search_visible(context):
    assert _page(context).is_new_launch_search_visible(), "New Launch search box should be visible."


@then("the New Launch search box should be empty")
def step_new_launch_search_empty(context):
    assert _page(context).get_search_box_value() == "", "New Launch search box should be empty."


@when("the user searches for the configured valid location")
def step_search_configured_valid_location(context):
    location = ConfigReader.get("new_launch", "location", "Noida")
    _page(context).search_valid_location(location)
    take_screenshot(context.driver, "bdd_valid_location_search")


@when("the user selects the configured location")
def step_select_configured_location(context):
    location = ConfigReader.get("new_launch", "location", "Noida")
    _page(context).search_location(location)
    take_screenshot(context.driver, "bdd_e2e_location_selected")


@then("the configured location should be selected")
def step_configured_location_selected(context):
    location = ConfigReader.get("new_launch", "location", "Noida")
    assert _page(context).is_location_selected(location), "Configured location should be selected."


@when("the user submits the New Launch search")
def step_submit_new_launch_search(context):
    _page(context).submit_search()
    take_screenshot(context.driver, "bdd_e2e_search_results_loaded")


@then("New Launch results should be displayed for the configured location")
def step_results_displayed_for_configured_location(context):
    location = ConfigReader.get("new_launch", "location", "Noida")
    assert _page(context).is_results_page_for_location(location), f"Results should be shown for {location}."
    assert _page(context).has_results_loaded(), "Results should load after search."


@when('the user enters partial location "{partial_location}"')
def step_enter_partial_location(context, partial_location):
    _page(context).enter_location_text(partial_location)
    context.suggestions = _page(context).get_visible_location_suggestions()
    take_screenshot(context.driver, "bdd_location_suggestions")


@then("location suggestions should be displayed")
def step_location_suggestions_displayed(context):
    assert context.suggestions, "Location suggestions should be displayed."


@then('the suggestions should include "{expected_location}"')
def step_suggestions_include_location(context, expected_location):
    assert any(
        expected_location.lower() in suggestion.lower()
        for suggestion in context.suggestions
    ), f"Suggestions should include {expected_location}."


@when("the user applies the Residential Property Type filter")
def step_apply_property_type_filter(context):
    _page(context).select_property_type()
    take_screenshot(context.driver, "bdd_property_type_filter")


@then('the "{filter_name}" filter should be applied')
def step_filter_should_be_applied(context, filter_name):
    assert _page(context).is_filter_applied(filter_name), f"{filter_name} filter should be applied."


@then("search results should remain loaded")
def step_search_results_should_remain_loaded(context):
    assert _page(context).has_results_loaded(), "Search results should remain loaded."


@when('the user enters invalid location "{invalid_location}"')
def step_enter_invalid_location(context, invalid_location):
    context.start_url = context.driver.current_url
    context.invalid_location = invalid_location
    _page(context).enter_location_text(invalid_location)
    take_screenshot(context.driver, "bdd_invalid_location")


@then("the invalid location should remain in the search box")
def step_invalid_location_remains(context):
    assert _page(context).get_search_box_value() == context.invalid_location


@then("valid location suggestions should not be displayed")
def step_valid_suggestions_not_displayed(context):
    assert not _page(context).has_visible_location_suggestions(timeout=5)


@then("the application should not navigate away from the New Launch search")
def step_application_should_not_navigate(context):
    assert context.driver.current_url == context.start_url


@when("the user clicks Search without entering a location")
def step_click_search_without_location(context):
    context.start_url = context.driver.current_url
    _page(context).click_search_without_waiting_for_results()
    take_screenshot(context.driver, "bdd_empty_location_search")


@when("the user applies the configured budget range filter")
def step_apply_configured_budget_filter(context):
    min_budget = ConfigReader.get("new_launch", "min_budget", "20 Lacs")
    max_budget = ConfigReader.get("new_launch", "max_budget", "80 Lacs")
    _page(context).select_budget_range(min_budget, max_budget)
    take_screenshot(context.driver, "bdd_e2e_budget_filter")


@when("the user applies the configured bedroom filter")
def step_apply_configured_bedroom_filter(context):
    bedroom = ConfigReader.get("new_launch", "bedroom", "2 BHK")
    _page(context).select_bedroom(bedroom)
    take_screenshot(context.driver, "bdd_e2e_bedroom_filter")


@then("the configured bedroom filter should be applied")
def step_configured_bedroom_filter_applied(context):
    bedroom = ConfigReader.get("new_launch", "bedroom", "2 BHK")
    assert _page(context).is_filter_applied(bedroom), f"{bedroom} filter should be applied."


@when("the user opens the first building from the result list")
def step_open_first_building(context):
    context.opened_project = _page(context).open_first_building_from_results()
    take_screenshot(context.driver, "bdd_e2e_building_detail_opened")


@then("the project detail page should be opened")
def step_project_detail_page_opened(context):
    assert context.opened_project, "Project name should be captured from the result card."
    assert _page(context).is_project_detail_page_opened(context.opened_project)


@when("the user closes the project disclaimer if it is visible")
def step_close_disclaimer_if_visible(context):
    context.details_page = PropertyDetailsPage(context.driver)
    if context.details_page.close_project_disclaimer_if_visible():
        take_screenshot(context.driver, "bdd_e2e_project_disclaimer_closed")


@when("the user clicks the View Number button")
def step_click_view_number(context):
    if not hasattr(context, "details_page"):
        context.details_page = PropertyDetailsPage(context.driver)
    assert context.details_page.click_view_number(), "Contact details or popup should appear after View Number."
    take_screenshot(context.driver, "bdd_e2e_view_number_popup")


@then("the contact details or contact form should be visible")
def step_contact_details_visible(context):
    assert context.details_page.is_contact_details_visible(), "Contact details or contact form should be visible."
