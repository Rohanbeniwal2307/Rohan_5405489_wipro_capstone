from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.filters_page import FiltersPage


class NewLaunchPage(FiltersPage):
    NEW_LAUNCH_TAB = (By.XPATH, "//*[@testid='NL']")
    SEARCH_BOX = (By.ID, "keyword2")
    FIRST_SUGGESTION = (By.XPATH, "//*[@id='0']")
    LOCATION_SUGGESTIONS = (
        By.XPATH,
        "//*[@id='0' or @id='1' or @id='2' or @id='3' or @id='4']",
    )
    SEARCH_BUTTON = (By.XPATH, "//*[@id='searchform_search_btn']/span")
    FIRST_PROJECT_LINK = (
        By.XPATH,
        "//a[contains(@href,'npxid') and normalize-space()]",
    )

    def __init__(self, driver):
        super().__init__(driver)
        self.wait = WebDriverWait(driver, 30)

    def open_new_launch_tab(self):
        self.click(self.NEW_LAUNCH_TAB)
        self.wait.until(EC.visibility_of_element_located(self.SEARCH_BOX))

    def is_new_launch_search_visible(self):
        return self.wait.until(EC.visibility_of_element_located(self.SEARCH_BOX)).is_displayed()

    def get_search_box_value(self):
        return self.wait.until(EC.visibility_of_element_located(self.SEARCH_BOX)).get_attribute("value")

    def enter_location_text(self, location):
        search = self.wait.until(EC.visibility_of_element_located(self.SEARCH_BOX))
        search.clear()
        search.send_keys(location)

    def get_visible_location_suggestions(self):
        self.wait.until(
            lambda driver: any(
                suggestion.is_displayed() and suggestion.text.strip()
                for suggestion in driver.find_elements(*self.LOCATION_SUGGESTIONS)
            )
        )
        return [
            suggestion.text.strip()
            for suggestion in self.driver.find_elements(*self.LOCATION_SUGGESTIONS)
            if suggestion.is_displayed() and suggestion.text.strip()
        ]

    def has_visible_location_suggestions(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: any(
                    suggestion.is_displayed() and suggestion.text.strip()
                    for suggestion in driver.find_elements(*self.LOCATION_SUGGESTIONS)
                )
            )
            return True
        except TimeoutException:
            return False

    def search_location(self, location):
        self.enter_location_text(location)

        suggestion = self.wait.until(EC.element_to_be_clickable(self.FIRST_SUGGESTION))
        suggestion.click()

    def click_search_without_waiting_for_results(self):
        search_button = self.wait.until(EC.presence_of_element_located(self.SEARCH_BUTTON))
        self.js_click(search_button)

    def submit_search(self):
        search_button = self.wait.until(EC.element_to_be_clickable(self.SEARCH_BUTTON))
        self.js_click(search_button)
        self.wait_for_results()

    def search_valid_location(self, location):
        self.search_location(location)
        self.submit_search()

    def is_results_page_for_location(self, location):
        page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        return location.lower() in self.driver.current_url.lower() or location.lower() in page_text

    def open_first_building_from_results(self):
        current_window = self.driver.current_window_handle
        current_url = self.driver.current_url

        project_link = self._get_first_visible_project_link()
        self.scroll_to_element(project_link)
        project_name = project_link.text.strip()
        self.js_click(project_link)

        self._switch_to_project_detail_window(current_window)
        self.wait.until(lambda driver: driver.current_url != current_url)
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        self.logger.info(f"Opened project detail page: {project_name}")
        return project_name

    def is_project_detail_page_opened(self, project_name):
        title = self.driver.title.lower()
        url = self.driver.current_url.lower()
        body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        normalized_project_name = project_name.lower()
        return (
            "npxid" in url
            and (normalized_project_name in title or normalized_project_name in body_text)
        )

    def _get_first_visible_project_link(self):
        self._nudge_lazy_loaded_results()
        return self.wait.until(
            lambda driver: next(
                (
                    link for link in driver.find_elements(*self.FIRST_PROJECT_LINK)
                    if link.is_displayed() and link.text.strip()
                ),
                False,
            )
        )

    def _switch_to_project_detail_window(self, original_window):
        try:
            WebDriverWait(self.driver, 8).until(lambda driver: len(driver.window_handles) > 1)
            for window_handle in self.driver.window_handles:
                if window_handle != original_window:
                    self.driver.switch_to.window(window_handle)
                    return
        except TimeoutException:
            self.driver.switch_to.window(original_window)

    # Backward-compatible method name used by the older test.
    def click_new_launch(self):
        self.open_new_launch_tab()

    # Backward-compatible method name used by the older test.
    def click_search_button(self):
        self.submit_search()
