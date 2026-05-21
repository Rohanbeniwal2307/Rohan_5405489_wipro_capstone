import pytest

from config.config_reader import ConfigReader
from pages.newlaunch_page import NewLaunchPage
from utilities.logger import Logger
from utilities.screenshot import take_screenshot


@pytest.mark.smoke
def test_open_newlaunch_module_from_homepage(setup):
    logger = Logger.get_logger()
    page = NewLaunchPage(setup)

    logger.info("TEST STARTED: open New Launch module")
    page.open_new_launch_tab()
    take_screenshot(setup, "positive_01_newlaunch_opened")

    assert page.is_new_launch_search_visible(), "New Launch search box should be visible."
    assert page.get_search_box_value() == "", "Search box should be empty when New Launch opens."


@pytest.mark.smoke
def test_search_valid_location_in_newlaunch(setup):
    logger = Logger.get_logger()
    location = ConfigReader.get("new_launch", "location", "Noida")
    page = NewLaunchPage(setup)

    logger.info("TEST STARTED: search valid location")
    page.open_new_launch_tab()
    page.search_valid_location(location)
    take_screenshot(setup, "positive_02_valid_location_search")

    assert page.is_results_page_for_location(location), f"Results page should show location: {location}."
    assert page.has_results_loaded(), "Search results or result summary should be visible."


@pytest.mark.smoke
def test_location_suggestions_display_for_partial_location(setup):
    logger = Logger.get_logger()
    page = NewLaunchPage(setup)

    logger.info("TEST STARTED: location suggestions")
    page.open_new_launch_tab()
    page.enter_location_text("Noi")
    suggestions = page.get_visible_location_suggestions()
    take_screenshot(setup, "positive_03_location_suggestions")

    assert suggestions, "Suggestions should be displayed for valid partial location."
    assert any("noida" in suggestion.lower() for suggestion in suggestions), "Suggestions should include Noida."


@pytest.mark.smoke
def test_residential_property_type_filter_applies_successfully(setup):
    logger = Logger.get_logger()
    location = ConfigReader.get("new_launch", "location", "Noida")
    page = NewLaunchPage(setup)

    logger.info("TEST STARTED: residential property type filter")
    page.open_new_launch_tab()
    page.search_valid_location(location)
    page.select_property_type()
    take_screenshot(setup, "positive_04_property_type_filter")

    assert page.is_filter_applied("Flat/Apartment"), "Flat/Apartment filter should be visible in Applied Filters."
    assert page.has_results_loaded(), "Results should remain loaded after applying property type filter."


@pytest.mark.regression
def test_invalid_location_does_not_show_valid_suggestions_or_proceed(setup):
    logger = Logger.get_logger()
    page = NewLaunchPage(setup)
    start_url = setup.current_url

    logger.info("TEST STARTED: invalid location negative case")
    page.open_new_launch_tab()
    page.enter_location_text("xyzabc123")
    take_screenshot(setup, "negative_01_invalid_location")

    assert page.get_search_box_value() == "xyzabc123", "Invalid text should remain in search box."
    assert not page.has_visible_location_suggestions(timeout=5), "Invalid location should not show valid suggestions."
    assert setup.current_url == start_url, "Invalid location should not navigate away from New Launch search."


@pytest.mark.regression
def test_search_does_not_proceed_without_location(setup):
    logger = Logger.get_logger()
    page = NewLaunchPage(setup)

    logger.info("TEST STARTED: empty location search negative case")
    page.open_new_launch_tab()
    start_url = setup.current_url
    page.click_search_without_waiting_for_results()
    take_screenshot(setup, "negative_02_empty_location_search")

    assert setup.current_url == start_url, "Empty location search should not navigate to results page."
    assert page.is_new_launch_search_visible(), "New Launch search should remain visible after empty search."
    assert page.get_search_box_value() == "", "Search box should still be empty."
