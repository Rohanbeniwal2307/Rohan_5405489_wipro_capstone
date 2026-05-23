from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utilities.base_page import BasePage


class FiltersPage(BasePage):
    PROPERTY_TYPE = (By.XPATH, "//*[@id='1']")
    BUDGET_MIN_DROPDOWN = (By.ID, "bdf__lfBudMin")
    BUDGET_MAX_DROPDOWN = (By.ID, "bdf__lf_budMax")
    BUDGET_MIN_VALUE = (By.CSS_SELECTOR, "#bdf__lfBudMin .bdf__minValue")
    BUDGET_MAX_VALUE = (By.CSS_SELECTOR, "#bdf__lf_budMax .bdf__maxValue")
    APPLIED_FILTERS_SECTION = (By.ID, "leftFilterSection")
    RESULT_SUMMARY = (
        By.XPATH,
        "//*[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'results') "
        "and contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'property')]",
    )
    RESULT_CONTAINER = (By.XPATH, "//*[@id='srp_tuple_list' or contains(@class,'srp')]")
    RESULT_ITEMS = (
        By.XPATH,
        "//*[contains(@id,'srp_tuple') "
        "or contains(@data-label,'SRP_CARD') "
        "or contains(@class,'srpTuple') "
        "or contains(@class,'projectTuple')]",
    )
    NO_RESULTS_MESSAGE = (
        By.XPATH,
        "//*[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no results') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no matching')]",
    )

    def select_property_type(self):
        result_container = self.wait_for_results()

        property_type = self.wait.until(EC.element_to_be_clickable(self.PROPERTY_TYPE))
        self.scroll_to_element(property_type)
        self.js_click(property_type)

        self.wait_for_results(previous_container=result_container)

    def select_budget_range(self, min_budget, max_budget):
        result_container = self.wait_for_results()

        self._select_budget_option(
            dropdown_locator=self.BUDGET_MIN_DROPDOWN,
            option_list_id="lf_budget_min_list",
            option_text=min_budget,
        )

        self._select_budget_option(
            dropdown_locator=self.BUDGET_MAX_DROPDOWN,
            option_list_id="lf_budget_max_list",
            option_text=max_budget,
        )
        self._wait_for_applied_budget_filter(min_budget, max_budget)
        self._wait_for_budget_results_refresh(result_container)

    def select_bedroom(self, bedroom):
        result_container = self.wait.until(EC.presence_of_element_located(self.RESULT_CONTAINER))

        bedroom_chip = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[@id='bedroom_num']"
                    "/ancestor::div[contains(@class,'accordion_content__accord_container')]"
                    f"//*[normalize-space()='{bedroom}']"
                    "/ancestor::*[contains(@class,'tags-and-chips__textOnly')][1]",
                )
            )
        )
        self.scroll_to_element(bedroom_chip)
        self.js_click(bedroom_chip)

        self._wait_for_applied_filter_text(bedroom)
        self._wait_for_budget_results_refresh(result_container)

    def _select_budget_option(self, dropdown_locator, option_list_id, option_text):
        dropdown = self.wait.until(EC.element_to_be_clickable(dropdown_locator))
        self.scroll_to_element(dropdown)
        self.js_click(dropdown)

        option = self.wait.until(
            lambda driver: next(
                (
                    item for item in driver.find_elements(
                        By.XPATH,
                        f"//*[@id='{option_list_id}']//li[normalize-space()='{option_text}']",
                    )
                    if item.is_displayed()
                ),
                False,
            )
        )
        self.scroll_to_element(option)
        self.js_click(option)

    def _wait_for_applied_budget_filter(self, min_budget, max_budget):
        try:
            WebDriverWait(self.driver, 10).until(
                lambda driver: (
                    min_budget in driver.find_element(*self.APPLIED_FILTERS_SECTION).text
                    and max_budget in driver.find_element(*self.APPLIED_FILTERS_SECTION).text
                )
            )
        except TimeoutException:
            self.logger.info("Budget dropdown values selected, but applied filter chips were slow to update.")

    def _wait_for_applied_filter_text(self, expected_text):
        self.wait.until(
            lambda driver: expected_text in driver.find_element(*self.APPLIED_FILTERS_SECTION).text
        )

    def get_applied_filters_text(self):
        return self.wait.until(
            EC.presence_of_element_located(self.APPLIED_FILTERS_SECTION)
        ).text

    def is_filter_applied(self, expected_text):
        return expected_text in self.get_applied_filters_text()

    def has_results_loaded(self):
        return self._results_or_empty_state_is_visible(self.driver) or self._result_summary_is_visible(self.driver)

    def _wait_for_budget_results_refresh(self, previous_container):
        try:
            WebDriverWait(self.driver, 15).until(
                lambda driver: (
                    self._results_or_empty_state_is_visible(driver)
                    or self._result_summary_is_visible(driver)
                )
            )
        except TimeoutException:
            self.logger.info("Filter applied, but result cards did not finish rendering in time.")

    def _result_summary_is_visible(self, driver):
        return any(
            summary.is_displayed() and summary.text.strip()
            for summary in driver.find_elements(*self.RESULT_SUMMARY)
        )

    def wait_for_results(self, previous_container=None):
        self.wait.until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

        if previous_container is not None:
            self._wait_for_results_refresh(previous_container)

        container = self.wait.until(EC.presence_of_element_located(self.RESULT_CONTAINER))
        self._nudge_lazy_loaded_results()
        self.wait.until(self._results_or_empty_state_is_visible)
        return container

    def _wait_for_results_refresh(self, previous_container):
        try:
            WebDriverWait(self.driver, 8).until(EC.staleness_of(previous_container))
        except Exception:
            self.logger.info("Result container did not go stale; waiting for result content.")

    def _nudge_lazy_loaded_results(self):
        self.driver.execute_script("window.scrollBy(0, 450);")
        self.driver.execute_script("window.scrollBy(0, -250);")

    def _results_or_empty_state_is_visible(self, driver):
        try:
            visible_results = [
                item for item in driver.find_elements(*self.RESULT_ITEMS)
                if self._is_real_result_card(item)
            ]
            if visible_results:
                return True

            visible_empty_messages = [
                message for message in driver.find_elements(*self.NO_RESULTS_MESSAGE)
                if message.is_displayed()
            ]
            return bool(visible_empty_messages)

        except StaleElementReferenceException:
            return False

    def _is_real_result_card(self, item):
        if not item.is_displayed():
            return False

        text = item.text.strip()
        if not text:
            return False

        lower_text = text.lower()
        listing_words = ("bhk", "resale", "builder", "owner", "possession", "carpet", "super built")
        return any(word in lower_text for word in listing_words)
