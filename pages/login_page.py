from selenium.webdriver.common.by import By
from .base_page import BasePage
import time

class LoginPage(BasePage):
    # Locators
    USER_INPUT = (By.NAME, "username")
    PASS_INPUT = (By.NAME, "password")
    LOGIN_BTN_TYPE = (By.XPATH, "//button[@type='submit']")
    LOGIN_BTN_TEXT = (By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Đăng nhập')]")

    def login_flow(self, username, password):
        """
        Hàm này tự kiểm tra:
        - Nếu thấy ô User -> Nhập và Login.
        - Nếu không thấy -> Coi như đã Login rồi, bỏ qua.
        """
        try:
            # Kiểm tra nhanh xem ô username có hiện không (chờ 3s thôi)
            if self.is_visible(self.USER_INPUT, timeout=3):
                print("-> Phát hiện chưa đăng nhập. Đang thực hiện Login...")
                
                # Gọi hàm enter_text (đã viết trong BasePage gồm xóa + điền)
                self.enter_text(self.USER_INPUT, username)
                self.enter_text(self.PASS_INPUT, password)
                
                # Thử bấm nút login
                try:
                    self.click(self.LOGIN_BTN_TYPE)
                except:
                    self.click(self.LOGIN_BTN_TEXT)
                
                # Chờ URL đổi sang dashboard
                time.sleep(3)
            else:
                print("-> Đã đăng nhập sẵn (Cookie). Bỏ qua bước Login.")
                
        except Exception as e:
            print(f"Lỗi trong quá trình login: {e}")