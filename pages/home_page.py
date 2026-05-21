from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from utilities.base_page import BasePage


class HomePage(BasePage):
    HEADER = (By.TAG_NAME, "header")

    def wait_until_loaded(self):
        self.wait.until(EC.presence_of_element_located(self.HEADER))

