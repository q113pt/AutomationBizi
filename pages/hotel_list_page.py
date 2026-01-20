from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base_page import BasePage
import time

class HotelListPage(BasePage):
    # --- LOCATORS ---
    MENU_HOTEL_LIST = (By.XPATH, "//span[contains(@class, 'ant-menu-title-content') and contains(text(), 'Hotel List')]")
    HOTEL_ID_INPUT = (By.NAME, "hotelId")
    SEARCH_BTN = (By.XPATH, "//button[contains(., 'Search') or contains(., 'Tìm kiếm') or @type='submit']")
    UPDATE_BTN = (By.XPATH, "//span[contains(@class, 'cursor-pointer') and (contains(., 'Update') or contains(., 'Cập nhật'))]")
    BODY = (By.TAG_NAME, "body")

    # --- ACTIONS ---
    def go_to_hotel_list_menu(self):
        """Click menu để reset trang"""
        print("   -> [Recovery] Click menu 'Hotel List'...")
        try:
            self.click(self.MENU_HOTEL_LIST)
            time.sleep(2)
        except:
            print("   ! Không click được Menu.")

    def search_hotel(self, hotel_id):
        """Tìm khách sạn"""
        print(f"   -> [Action] Tìm ID: {hotel_id}")
        try:
            # Chờ ô input xuất hiện
            element = self.wait.until(lambda d: d.find_element(*self.HOTEL_ID_INPUT))
        except:
            # Nếu ko thấy, click menu để reload
            self.go_to_hotel_list_menu()
            element = self.wait.until(lambda d: d.find_element(*self.HOTEL_ID_INPUT))

        # Xóa và nhập
        element.click()
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        time.sleep(0.1)
        element.send_keys(hotel_id)
        
        self.click(self.SEARCH_BTN)
        time.sleep(2) # Chờ kết quả

    def open_update_form(self):
        """Mở form Update"""
        self.click(self.UPDATE_BTN)

    def close_update_form(self):
        """Đóng form (ESC)"""
        try:
            self.driver.find_element(*self.BODY).send_keys(Keys.ESCAPE)
            time.sleep(1)
        except:
            pass