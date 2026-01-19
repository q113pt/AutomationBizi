# pages/base_page.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def click(self, by_locator):
        # Tự động chờ nút bấm được rồi mới click
        element = self.wait.until(EC.element_to_be_clickable(by_locator))
        element.click()

    def enter_text(self, by_locator, text):
        # Tự động chờ, tự động xóa sạch kiểu React, rồi mới điền
        element = self.wait.until(EC.visibility_of_element_located(by_locator))
        element.click()
        element.send_keys(Keys.CONTROL + "a") # Bôi đen
        element.send_keys(Keys.DELETE)        # Xóa
        element.send_keys(text)               # Điền

    def get_text(self, by_locator):
        element = self.wait.until(EC.visibility_of_element_located(by_locator))
        return element.text

    # --- HÀM MỚI THÊM VÀO ---
    def is_visible(self, by_locator, timeout=5):
        """Kiểm tra xem phần tử có hiện lên không (trả về True/False)"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(by_locator)
            )
            return True
        except TimeoutException:
            return False