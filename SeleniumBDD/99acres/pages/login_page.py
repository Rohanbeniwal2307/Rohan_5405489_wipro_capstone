from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config_reader import ConfigReader
from utilities.base_page import BasePage


class LoginPage(BasePage):
    USER_ICON = (
        By.XPATH,
        "//i[contains(@class,'icon_userWhite') and contains(@class,'theader__dot')]",
    )
    LOGIN_REGISTER = (
        By.XPATH,
        "//*[contains(text(),'LOGIN / REGISTER') or contains(text(),'Login / Register')]",
    )
    PHONE_INPUT = (By.XPATH, "//input[@data-for='phnNumber']")
    NEW_LAUNCH_TAB = (By.XPATH, "//*[@testid='NL']")
    CONTINUE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Continue' or .//*[normalize-space()='Continue']]"
        "|//*[@role='button' and (normalize-space()='Continue' or .//*[normalize-space()='Continue'])]"
        "|//*[normalize-space()='Continue']/ancestor::*[self::button or @role='button'][1]",
    )
    LOGIN_DIALOG = (
        By.XPATH,
        "//*[contains(@class,'component__dialogueBox') "
        "and contains(normalize-space(.),'Login / Register')]",
    )
    LOGIN_OR_OTP_OVERLAY = (
        By.XPATH,
        "//*[contains(@class,'component__dialogueBox') "
        "or @data-for='phnNumber' "
        "or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'otp') "
        "or ((self::div or self::span or self::label or self::p) "
        "and contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'enter otp'))]",
    )
    HOME_READY = (
        By.XPATH,
        "//*[@testid='NL' or self::header or contains(normalize-space(.),'New Launch')]",
    )

    def open_login_popup(self):
        icon = self.wait.until(EC.presence_of_element_located(self.USER_ICON))
        ActionChains(self.driver).move_to_element(icon).perform()

        login_register = self.wait.until(EC.presence_of_element_located(self.LOGIN_REGISTER))
        self.js_click(login_register)

        phone_input = self.wait.until(EC.presence_of_element_located(self.PHONE_INPUT))
        self.driver.execute_script("arguments[0].focus();", phone_input)
        phone_input.clear()
        phone_input.send_keys(ConfigReader.get("login", "phone_number"))

        continue_button = self.wait.until(EC.element_to_be_clickable(self.CONTINUE_BUTTON))
        self.js_click(continue_button)

    def wait_for_manual_login_and_return_home(self):
        print("\nLogin popup is open in Chrome.")
        print("Phone number is filled automatically. Enter OTP and finish login.")
        print("Automation will continue automatically after login completes.\n")

        wait_seconds = ConfigReader.getint("login", "manual_wait_seconds", 300)
        try:
            WebDriverWait(self.driver, wait_seconds).until(self._manual_login_completed)
        except TimeoutException:
            self.logger.error(f"Manual login did not complete within {wait_seconds} seconds.")
            raise

        self.logger.info("Manual OTP completed by user; returning to homepage.")
        self.driver.get(ConfigReader.get("application", "base_url"))
        self.wait.until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        self.wait.until(EC.element_to_be_clickable(self.NEW_LAUNCH_TAB))
        self.wait.until(EC.presence_of_element_located(self.HOME_READY))

    def login_manually_and_return_home(self):
        self.open_login_popup()
        self.wait_for_manual_login_and_return_home()

    def _manual_login_completed(self, driver):
        if driver.execute_script("return document.readyState") != "complete":
            return False

        visible_overlays = [
            element
            for element in driver.find_elements(*self.LOGIN_OR_OTP_OVERLAY)
            if element.is_displayed()
        ]
        if visible_overlays:
            return False

        return bool(driver.find_elements(*self.HOME_READY))

    def _wait_until_login_popup_closes(self, wait_seconds):
        try:
            WebDriverWait(self.driver, wait_seconds).until_not(
                EC.presence_of_element_located(self.LOGIN_DIALOG)
            )
        except Exception:
            self.logger.info("Login popup was still visible after manual wait; continuing after user confirmation.")
