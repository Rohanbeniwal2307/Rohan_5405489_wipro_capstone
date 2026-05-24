import re
from time import sleep

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config_reader import ConfigReader
from utilities.base_page import BasePage


class PropertyDetailsPage(BasePage):
    DISCLAIMER_OK_BUTTON = (
        By.XPATH,
        "//*[normalize-space()='OK, Got it' or normalize-space()='Ok, Got it']",
    )
    VIEW_NUMBER_BUTTON = (
        By.XPATH,
        "("
        "//button[normalize-space()='View Number' or .//*[normalize-space()='View Number']]"
        "|//a[normalize-space()='View Number' or .//*[normalize-space()='View Number']]"
        "|//*[@role='button' and (normalize-space()='View Number' or .//*[normalize-space()='View Number'])]"
        "|//*[normalize-space()='View Number']/ancestor::*[self::button or self::a or @role='button'][1]"
        ")[1]",
    )
    CONTACT_POPUP = (
        By.XPATH,
        "//*[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'please share your details') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'basic information') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'are you a property dealer') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'phone number') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'login') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'register') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'otp')]",
    )
    BUYING_TIMELINE_QUESTION = (
        By.XPATH,
        "//*[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
        "'when are you planning to buy this property')]",
    )
    THREE_MONTHS_OPTION = (
        By.XPATH,
        "//*[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'3 month') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'three month')]"
        "/ancestor-or-self::*[self::button or self::label or self::li or @role='button' or @role='radio'][1]",
    )
    CONTACT_FORM_VIEW_NUMBER_BUTTON = (
        By.XPATH,
        "("
        "//button[normalize-space()='View Number' or .//*[normalize-space()='View Number']]"
        "|//*[@role='button' and (normalize-space()='View Number' or .//*[normalize-space()='View Number'])]"
        "|//*[normalize-space()='View Number']/ancestor::*[self::button or @role='button'][1]"
        ")[last()]",
    )
    CONTACT_NAME_INPUT = (
        By.XPATH,
        "//input["
        "contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'name') "
        "or contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'name') "
        "or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'name')"
        "]",
    )
    CONTACT_EMAIL_INPUT = (
        By.XPATH,
        "//input["
        "@type='email' "
        "or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email') "
        "or contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email') "
        "or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email')"
        "]",
    )
    CONTACT_PHONE_INPUT = (
        By.XPATH,
        "//input["
        "@type='tel' "
        "or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'phone') "
        "or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'mobile') "
        "or contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'phone') "
        "or contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'mobile') "
        "or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'phone') "
        "or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'mobile')"
        "]",
    )
    PROPERTY_DEALER_NO_OPTION = (
        By.XPATH,
        "//*[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'are you a property dealer')]"
        "/following::*[normalize-space()='No' or normalize-space()='NO'][1]"
        "/ancestor-or-self::*[self::button or self::label or self::li or @role='button' or @role='radio'][1]",
    )

    def __init__(self, driver):
        super().__init__(driver)
        self._cached_view_number_button = None

    def click_view_number(self):
        button = self._get_cached_or_find_view_number_button()
        self.scroll_to_element(button)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            button,
        )
        sleep(0.25)
        self._dispatch_mouse_click(button)
        self.logger.info("View Number button clicked; waiting for contact popup.")
        if not self._contact_popup_appears_quickly():
            try:
                button.click()
            except (ElementClickInterceptedException, StaleElementReferenceException):
                ActionChains(self.driver).move_to_element(button).pause(0.1).click(button).perform()
        self._wait_for_contact_details(button)
        self.complete_contact_form_for_view_number()
        sleep(5)
        return self.is_contact_details_visible()

    def complete_contact_form_for_view_number(self):
        if not self._contact_popup_appears_quickly():
            return False

        self._fill_visible_input(self.CONTACT_NAME_INPUT, ConfigReader.get("contact", "name", "Test User"))
        self._fill_visible_input(
            self.CONTACT_EMAIL_INPUT,
            ConfigReader.get("contact", "email", "testuser@example.com"),
        )
        self._fill_visible_input(
            self.CONTACT_PHONE_INPUT,
            ConfigReader.get("contact", "phone_number", ConfigReader.get("login", "phone_number")),
        )
        self.select_property_dealer_no_if_visible()
        self.select_three_month_buying_timeline_if_visible()
        return self.click_contact_form_view_number_if_visible()

    def select_three_month_buying_timeline_if_visible(self):
        if not self._buying_timeline_question_is_visible():
            return False

        option = WebDriverWait(self.driver, 5).until(
            lambda driver: self._first_visible_element(self.THREE_MONTHS_OPTION)
        )
        self.scroll_to_element(option)
        self._safe_click(option)
        self.logger.info("Selected 3 months for property buying timeline.")
        return True

    def click_contact_form_view_number_if_visible(self):
        try:
            view_number_button = WebDriverWait(self.driver, 5).until(
                lambda driver: self._first_visible_element(self.CONTACT_FORM_VIEW_NUMBER_BUTTON)
            )
        except TimeoutException:
            return False

        self.scroll_to_element(view_number_button)
        self._safe_click(view_number_button)
        self.logger.info("Clicked View Number after filling contact form.")
        self._wait_for_contact_details(view_number_button)
        return True

    def select_property_dealer_no_if_visible(self):
        option = self._first_visible_element(self.PROPERTY_DEALER_NO_OPTION)
        if not option:
            return False

        self.scroll_to_element(option)
        self._safe_click(option)
        self.logger.info("Selected No for property dealer question.")
        return True

    def _fill_visible_input(self, locator, value):
        field = self._first_visible_input(locator)
        if not field:
            return False

        current_value = field.get_attribute("value") or ""
        if current_value.strip():
            return False

        self.scroll_to_element(field)
        field.clear()
        field.send_keys(value)
        self.logger.info(f"Filled contact form field: {locator}")
        return True

    def _first_visible_input(self, locator):
        for element in self.driver.find_elements(*locator):
            try:
                if element.is_displayed() and element.is_enabled():
                    return element
            except StaleElementReferenceException:
                continue
        return False

    def _dispatch_mouse_click(self, button):
        self.driver.execute_script(
            """
            const element = arguments[0];
            const rect = element.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;
            const target = document.elementFromPoint(x, y) || element;
            ['mouseover', 'mousedown', 'mouseup', 'click'].forEach(type => {
                target.dispatchEvent(new MouseEvent(type, {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: x,
                    clientY: y
                }));
            });
            """,
            button,
        )

    def _safe_click(self, element):
        try:
            element.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            self.js_click(element)

    def is_view_number_visible(self):
        self._cached_view_number_button = self._find_view_number_button()
        return self._cached_view_number_button is not None

    def is_contact_details_visible(self):
        return self._dealer_number_or_contact_popup_is_visible(self.driver)

    def close_project_disclaimer_if_visible(self):
        try:
            has_visible_ok_button = any(
                button.is_displayed()
                for button in self.driver.find_elements(*self.DISCLAIMER_OK_BUTTON)
            )
        except StaleElementReferenceException:
            has_visible_ok_button = True

        if not has_visible_ok_button:
            return False

        for _ in range(2):
            try:
                ok_button = WebDriverWait(self.driver, 2).until(
                    lambda driver: next(
                        (
                            button for button in driver.find_elements(*self.DISCLAIMER_OK_BUTTON)
                            if button.is_displayed()
                        ),
                        False,
                    )
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                    ok_button,
                )
                try:
                    ok_button.click()
                except (ElementClickInterceptedException, StaleElementReferenceException):
                    self.js_click(ok_button)

                WebDriverWait(self.driver, 5).until(
                    lambda driver: not any(
                        button.is_displayed()
                        for button in driver.find_elements(*self.DISCLAIMER_OK_BUTTON)
                    )
                )
                return True
            except (StaleElementReferenceException, TimeoutException):
                sleep(1)

        return False

    def _wait_for_contact_details(self, clicked_button=None):
        try:
            WebDriverWait(self.driver, 6).until(
                lambda driver: (
                    self._contact_popup_is_visible_fast(driver)
                    or self._dealer_number_or_contact_popup_is_visible(driver)
                    or self._view_number_button_changed(driver, clicked_button)
                )
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
            for text in (
                "please share your details",
                "view number",
                "basic information",
                "optional information",
                "are you a property dealer",
                "phone number",
                "mobile number",
                "enter your phone",
                "otp",
                "login",
                "register",
            )
        )
        return has_phone_number or has_contact_state

    def _contact_popup_is_visible_fast(self, driver):
        try:
            return any(
                element.is_displayed() and element.text.strip()
                for element in driver.find_elements(*self.CONTACT_POPUP)
            )
        except StaleElementReferenceException:
            return False

    def _contact_popup_appears_quickly(self):
        try:
            WebDriverWait(self.driver, 2).until(self._contact_popup_is_visible_fast)
            return True
        except TimeoutException:
            return False

    def _view_number_button_changed(self, driver, clicked_button):
        if clicked_button is None:
            return False
        try:
            if not clicked_button.is_displayed():
                return True
            return clicked_button.text.strip().lower() != "view number"
        except StaleElementReferenceException:
            return True

    def _get_visible_contact_popup_text(self, driver):
        texts = []
        for element in driver.find_elements(*self.CONTACT_POPUP):
            try:
                if element.is_displayed() and element.text.strip():
                    texts.append(element.text.strip())
            except StaleElementReferenceException:
                continue
        return " ".join(texts)

    def _buying_timeline_question_is_visible(self):
        try:
            WebDriverWait(self.driver, 3).until(
                lambda driver: self._first_visible_element(self.BUYING_TIMELINE_QUESTION)
            )
            return True
        except TimeoutException:
            return False

    def _first_visible_element(self, locator):
        for element in self.driver.find_elements(*locator):
            try:
                if element.is_displayed() and element.text.strip():
                    return element
            except StaleElementReferenceException:
                continue
        return False

    def _find_view_number_button(self):
        self.close_project_disclaimer_if_visible()
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for _ in range(3):
            try:
                button = WebDriverWait(self.driver, 2).until(
                    lambda driver: self._first_visible_view_number_button()
                )
                return button
            except (StaleElementReferenceException, TimeoutException):
                pass

            self.driver.execute_script("window.scrollBy(0, Math.floor(window.innerHeight * 0.75));")
            sleep(0.5)
            current_height = self.driver.execute_script("return document.body.scrollHeight")
            if current_height == last_height:
                continue
            last_height = current_height

        raise TimeoutException("View Number or contact button was not found on the project detail page.")

    def _get_cached_or_find_view_number_button(self):
        try:
            if self._cached_view_number_button and self._cached_view_number_button.is_displayed():
                return self._cached_view_number_button
        except StaleElementReferenceException:
            self._cached_view_number_button = None

        self._cached_view_number_button = self._find_view_number_button()
        return self._cached_view_number_button

    def _first_visible_view_number_button(self):
        for button in self.driver.find_elements(*self.VIEW_NUMBER_BUTTON):
            try:
                if button.is_displayed() and button.text.strip():
                    return button
            except StaleElementReferenceException:
                continue
        return False
