import re
from time import sleep

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utilities.base_page import BasePage


class PropertyDetailsPage(BasePage):
    VIEW_NUMBER_BUTTON = (
        By.XPATH,
        "(//button[contains(@class,'ProjectInfo__viewNumberButton') "
        "or .//*[normalize-space()='View Number'] "
        "or normalize-space()='View Number'])[1]",
    )
    CONTACT_POPUP = (
        By.XPATH,
        "//*[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'phone number') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'login') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'register') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'otp')]",
    )

    def click_view_number(self):
        button = self.wait.until(EC.presence_of_element_located(self.VIEW_NUMBER_BUTTON))
        self.scroll_to_element(button)
        self.js_click(button)
        self._wait_for_contact_details()
        sleep(5)
        return self.is_contact_details_visible()

    def is_view_number_visible(self):
        return self.wait.until(EC.presence_of_element_located(self.VIEW_NUMBER_BUTTON)).is_displayed()

    def is_contact_details_visible(self):
        return self._dealer_number_or_contact_popup_is_visible(self.driver)

    def _wait_for_contact_details(self):
        try:
            WebDriverWait(self.driver, 15).until(
                lambda driver: self._dealer_number_or_contact_popup_is_visible(driver)
            )
        except TimeoutException:
            self.logger.info("View Number clicked, but dealer contact details did not render in time.")

    def _dealer_number_or_contact_popup_is_visible(self, driver):
        visible_text = self._get_visible_contact_popup_text(driver)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        combined_text = f"{visible_text} {body_text}"

        has_phone_number = re.search(r"(\+91[\s-]?)?[6-9]\d{9}", combined_text) is not None
        has_contact_state = any(
            text in combined_text.lower()
            for text in ("dealer", "builder", "contact", "phone number", "view number")
        )
        return has_phone_number or has_contact_state

    def _get_visible_contact_popup_text(self, driver):
        texts = []
        for element in driver.find_elements(*self.CONTACT_POPUP):
            try:
                if element.is_displayed() and element.text.strip():
                    texts.append(element.text.strip())
            except StaleElementReferenceException:
                continue
        return " ".join(texts)
