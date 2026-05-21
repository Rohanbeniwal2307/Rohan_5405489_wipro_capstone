import pytest

from config.config_reader import ConfigReader
from pages.login_page import LoginPage
from pages.newlaunch_page import NewLaunchPage
from pages.property_details_page import PropertyDetailsPage
from utilities.logger import Logger
from utilities.screenshot import take_screenshot


def test_login():
    print("Login test running")


@pytest.mark.regression
def test_newlaunch_end_to_end_flow(setup):
    logger = Logger.get_logger()
    driver = setup
    location = ConfigReader.get("new_launch", "location", "Noida")
    min_budget = ConfigReader.get("new_launch", "min_budget", "20 Lacs")
    max_budget = ConfigReader.get("new_launch", "max_budget", "80 Lacs")
    bedroom = ConfigReader.get("new_launch", "bedroom", "2 BHK")

    logger.info("TEST STARTED: New Launch end-to-end flow")

    if ConfigReader.getboolean("end_to_end", "login_enabled", fallback=False):
        login_page = LoginPage(driver)
        take_screenshot(driver, "e2e_login_home_before_popup")
        login_page.login_manually_and_return_home()
        logger.info("Manual login completed")
        take_screenshot(driver, "e2e_login_completed_home")
        assert ConfigReader.get("application", "base_url") in driver.current_url

    page = NewLaunchPage(driver)

    page.open_new_launch_tab()
    logger.info("Clicked New Launch")
    take_screenshot(driver, "e2e_new_launch_tab_clicked")
    assert page.is_new_launch_search_visible(), "New Launch search box should be visible."

    page.search_location(location)
    logger.info("Entered location")
    take_screenshot(driver, "e2e_location_entered")
    assert location.lower() in page.get_search_box_value().lower(), "Selected location should appear in search box."

    page.submit_search()
    logger.info("Search clicked")
    take_screenshot(driver, "e2e_search_results_loaded")
    assert page.is_results_page_for_location(location), f"Results should be shown for {location}."
    assert page.has_results_loaded(), "Results should load after search."

    page.select_property_type()
    logger.info("Property type selected")
    take_screenshot(driver, "e2e_filter_property_type")
    assert page.is_filter_applied("Flat/Apartment"), "Property type filter should be applied."

    page.select_budget_range(min_budget, max_budget)
    logger.info("Budget filter selected")
    take_screenshot(driver, "e2e_filter_budget")
    assert page.has_results_loaded(), "Results should stay available after applying budget filter."

    page.select_bedroom(bedroom)
    logger.info("Bedroom filter selected")
    take_screenshot(driver, "e2e_filter_bedroom")
    assert page.is_filter_applied(bedroom), f"{bedroom} filter should be applied."

    opened_project = page.open_first_building_from_results()
    logger.info(f"Opened building: {opened_project}")
    take_screenshot(driver, "e2e_building_detail_opened")
    assert opened_project, "Project name should be captured from the result card."
    assert page.is_project_detail_page_opened(opened_project), "Project detail page should open."

    details_page = PropertyDetailsPage(driver)
    assert details_page.is_view_number_visible(), "View Number button should be visible on detail page."
    assert details_page.click_view_number(), "Contact details or login/contact popup should appear after View Number."
    logger.info("Clicked View Number")
    take_screenshot(driver, "e2e_view_number_popup")

    logger.info("TEST COMPLETED: New Launch end-to-end flow")
