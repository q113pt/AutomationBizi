from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base_page import BasePage
import time

class InventoryPage(BasePage):
    # --- 1. ĐỊNH NGHĨA LOCATORS (ĐỊA CHỈ PHẦN TỬ) ---
    
    # Menu
    MENU_TAB = (By.XPATH, "//span[contains(text(), 'Room Inventory Management') or contains(text(), 'Quản lý tồn kho phòng')]")
    
    # Ô nhập liệu
    HOTEL_ID_INPUT = (By.NAME, "hotelId")
    
    # Nút Search (Thường vẫn là button, giữ nguyên hoặc dùng //* để tìm tất cả thẻ)
    SEARCH_BTN = (By.XPATH, "//*[contains(text(), 'Search') or contains(text(), 'Tìm kiếm') or @type='submit']")
    
    # [ĐÃ SỬA] Nút Update là thẻ SPAN, không phải BUTTON
    # Logic: Tìm thẻ <span> có chứa chữ 'Update' hoặc 'Cập nhật' VÀ có class 'cursor-pointer' (để chắc chắn là nút bấm)
    UPDATE_BTN = (By.XPATH, "//span[contains(@class, 'cursor-pointer') and (contains(., 'Update') or contains(., 'Cập nhật'))]")
    
    # Popup items
    ON_REQUEST_BTN = (By.XPATH, "//button[contains(text(), 'On Request')]")
    AVAILABLE_OPT = (By.XPATH, "//li[contains(text(), 'Available')]")
    
    BODY = (By.TAG_NAME, "body")

    # --- 2. HÀNH ĐỘNG ---

    def go_to_inventory_menu(self):
        print("-> [Flow] Chuyển trang...")
        self.click(self.MENU_TAB)
        # Tăng tốc độ: Chờ ô input xuất hiện thay vì sleep cứng
        try:
            self.wait.until(lambda d: d.find_element(*self.HOTEL_ID_INPUT))
        except:
            time.sleep(1) 

    def search_hotel(self, hotel_id):
        """Nhập ID và bấm tìm kiếm"""
        # 1. Tìm và thao tác input
        element = self.wait.until(lambda d: d.find_element(*self.HOTEL_ID_INPUT))
        
        element.click()
        # Combo xóa sạch
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        time.sleep(0.1) 
        
        element.send_keys(hotel_id)
        
        # 2. Click tìm kiếm
        self.click(self.SEARCH_BTN)
        
        # Chờ bảng tải lại (Quan trọng)
        time.sleep(2.5) 

    def open_update_form(self):
        """Mở form cập nhật"""
        print("   -> [Action] Tìm nút Update...")
        try:
            # Thử click lần 1
            self.click(self.UPDATE_BTN)
            print("   -> Đã click Update.")
            time.sleep(1.5) 
        except Exception:
            print("   ! Click trượt (do loading), thử lại...")
            time.sleep(1)
            # Tìm lại và click lần 2
            btn = self.driver.find_element(*self.UPDATE_BTN)
            btn.click()
            time.sleep(1.5)

    def close_update_form(self):
        print("   -> Đóng form.")
        self.driver.find_element(*self.BODY).send_keys(Keys.ESCAPE)
        time.sleep(0.5)

    def change_all_request_to_available(self):
        print("      -> Quét 'On Request'...")
        while True:
            try:
                # Tìm nút On Request đầu tiên
                btn = self.driver.find_element(*self.ON_REQUEST_BTN)
                btn.click()
                time.sleep(0.3) 
                
                self.click(self.AVAILABLE_OPT)
                print("      + Done 1 item")
                time.sleep(0.3)
            except Exception:
                print("      -> Hết.")
                break