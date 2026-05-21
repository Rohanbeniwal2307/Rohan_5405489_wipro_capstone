from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
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
    LOGIN_DIALOG = (
        By.XPATH,
        "//*[contains(@class,'component__dialogueBox') "
        "and contains(normalize-space(.),'Login / Register')]",
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

    def wait_for_manual_login_and_return_home(self):
        wait_seconds = ConfigReader.getint("login", "manual_wait_seconds", 300)
        print("\nLogin popup is open in Chrome.")
        print("Enter your phone number, click Continue, enter OTP, and finish login.")
        print("After login completes, press ENTER here to continue to New Launch.\n")
        input("Press ENTER after completing login and OTP...")

        self._wait_until_login_popup_closes(wait_seconds)
        self.driver.get(ConfigReader.get("application", "base_url"))
        self.wait.until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        self.wait.until(EC.presence_of_element_located(self.HOME_READY))

    def login_manually_and_return_home(self):
        self.open_login_popup()
        self.wait_for_manual_login_and_return_home()

    def _wait_until_login_popup_closes(self, wait_seconds):
        try:
            WebDriverWait(self.driver, wait_seconds).until_not(
                EC.presence_of_element_located(self.LOGIN_DIALOG)
            )
        except Exception:
            self.logger.info("Login popup was still visible after manual wait; continuing after user confirmation.")
