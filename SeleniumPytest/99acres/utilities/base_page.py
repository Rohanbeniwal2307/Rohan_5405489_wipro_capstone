from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utilities.logger import Logger


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
        self.logger = Logger.get_logger()

    def click(self, locator):
        for attempt in range(3):
            try:
                self.logger.info(f"Clicking on element: {locator}")
                element = self.wait.until(EC.element_to_be_clickable(locator))
                element.click()
                self.logger.info(f"Clicked successfully: {locator}")
                return
            except StaleElementReferenceException:
                if attempt == 2:
                    raise
                self.logger.info(f"Element went stale, retrying click: {locator}")
        self.logger.error(f"Click failed on {locator}")

    def type(self, locator, value):
        try:
            self.logger.info(f"Entering text in: {locator}")
            element = self.wait.until(EC.visibility_of_element_located(locator))
            element.clear()
            element.send_keys(value)
            self.logger.info(f"Text entered successfully in: {locator}")
        except Exception as error:
            self.logger.error(f"Type failed on {locator} | Error: {error}")
            raise

    def get_title(self):
        title = self.driver.title
        self.logger.info(f"Page title fetched: {title}")
        return title

    def get_text(self, locator):
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            text = element.text
            self.logger.info(f"Text fetched: {text}")
            return text
        except Exception as error:
            self.logger.error(f"Get text failed on {locator} | Error: {error}")
            raise

    def scroll_to_element(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            element,
        )

    def js_click(self, element):
        self.driver.execute_script("arguments[0].click();", element)
