from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
import time

class RoomUpdatePage(BasePage):
    # --- LOCATORS ---
    ROOM_TAB = (By.XPATH, "//button[contains(., 'ROOM MANAGEMENT') or contains(., 'Quản lý phòng')]")
    ADD_ROOM_BTN = (By.XPATH, "//button[contains(., 'ADD ROOM')]")
    # Nút UPDATE chuẩn
    UPDATE_SUBMIT_BTN = (By.XPATH, "//button[@type='submit']//div[normalize-space()='UPDATE'] | //button[normalize-space()='UPDATE']")

    # --- HELPERS ---
    def scroll_to_element(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)
        except:
            pass

    def force_click(self, element):
        """Click bằng Javascript nếu click thường thất bại"""
        try:
            element.click()
        except:
            self.driver.execute_script("arguments[0].click();", element)

    def handle_combobox(self, element, text_to_type="o", name="Dropdown"):
        """Scroll -> Click -> Nhập text -> Chờ -> Enter"""
        try:
            self.scroll_to_element(element)
            self.force_click(element)
            time.sleep(0.5)
            
            element.send_keys(text_to_type)
            time.sleep(2) # Chờ load list
            
            element.send_keys(Keys.ENTER)
            time.sleep(1) 
        except Exception as e:
            print(f"      ! Lỗi xử lý {name}: {e}")

    # --- ACTIONS ---

    def click_room_management_tab(self):
        print("   -> [Action] Click tab ROOM MANAGEMENT...")
        time.sleep(2)
        try:
            # Chờ nút xuất hiện và click
            btn = self.wait.until(EC.element_to_be_clickable(self.ROOM_TAB))
            self.force_click(btn)
            print("   -> Đã click Tab. Chờ 3s cho form load...")
            time.sleep(3) # Chờ form trượt ra hết
        except Exception as e:
            print(f"   ! Lỗi click tab: {e}")
            raise e

    def submit_update(self):
        print("      -> [Action] Nhấn nút UPDATE (Submit)...")
        try:
            btns = self.driver.find_elements(By.XPATH, "//button[contains(., 'UPDATE')]")
            target_btn = None
            for btn in btns:
                text = btn.text.upper()
                if "UPDATE" in text and "STATUS" not in text and "CONTENT" not in text:
                    target_btn = btn
                    break
            
            if target_btn:
                self.scroll_to_element(target_btn)
                self.force_click(target_btn)
                time.sleep(4) 
            else:
                print("      ! Không tìm thấy nút UPDATE chuẩn.")
        except Exception as e:
            print(f"      ! Lỗi nhấn nút Update: {e}")

    def add_new_room(self):
        print("      -> [Action] Nhấn ADD ROOM...")
        try:
            btn = self.driver.find_element(*self.ADD_ROOM_BTN)
            self.scroll_to_element(btn)
            self.force_click(btn)
            time.sleep(2) 
        except Exception as e:
            print(f"      ! Lỗi click Add Room: {e}")

    def enter_text_element(self, element, text):
        self.scroll_to_element(element)
        self.force_click(element)
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(text)

    # --- ĐIỀN DỮ LIỆU ---

    def fill_first_room_basic(self, area="25"):
        """
        Hàm này được gọi ở dòng 43 trong file Test của bạn.
        Nó sẽ tìm ô Area, Amenities, View ĐẦU TIÊN (của phòng 1) để nhập.
        """
        print("      -> [Input Room 1] Nhập Area, Amenities, View...")
        try:
            # 1. Nhập Area
            # Tìm input Area đầu tiên [1]
            area_loc = (By.XPATH, "(//input[contains(@placeholder, 'Area') or contains(@name, 'squareMeters')])[1]")
            area_input = self.wait.until(EC.visibility_of_element_located(area_loc))
            self.enter_text_element(area_input, area)
            
            # 2. Amenities (Room 1)
            print("         - Chọn Amenities (Room 1)...")
            # Tìm ô Amenities đầu tiên [1]
            am_loc = (By.XPATH, "(//input[@placeholder='Select room amenities'])[1]")
            am_input = self.wait.until(EC.presence_of_element_located(am_loc))
            self.handle_combobox(am_input, "o", "Amenities")

            # 3. View (Room 1)
            print("         - Chọn View (Room 1)...")
            # Tìm ô View đầu tiên [1]
            view_loc = (By.XPATH, "(//input[@placeholder='Select view'])[1]")
            view_input = self.wait.until(EC.presence_of_element_located(view_loc))
            self.handle_combobox(view_input, "o", "View")

        except Exception as e:
            print(f"      ! Lỗi nhập phòng 1: {e}")

    def fill_last_new_room(self, name_vi="Phòng Mới", name_en="New Room", area="30", max_occ="3", adult="2", child="2"):
        print("      -> [Input New Room] Nhập Full Info...")
        try:
            time.sleep(1) # Chờ DOM cập nhật sau khi Add Room

            # 1. Nhập Tên
            name_vis = self.driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'Vietnamese')]")
            if name_vis: self.enter_text_element(name_vis[-1], name_vi)
            
            name_ens = self.driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'English')]")
            if name_ens: self.enter_text_element(name_ens[-1], name_en)

            # 2. Nhập Area
            areas = self.driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'Area') or contains(@name, 'squareMeters')]")
            if areas: self.enter_text_element(areas[-1], area)

            # 3. Amenities (Room Mới - lấy cái cuối cùng [-1])
            amenities = self.driver.find_elements(By.XPATH, "//input[@placeholder='Select room amenities']")
            if amenities:
                print("         - Chọn Amenities (Room Mới)...")
                self.handle_combobox(amenities[-1], "o", "Amenities")

            # 4. View (Room Mới - lấy cái cuối cùng [-1])
            views = self.driver.find_elements(By.XPATH, "//input[@placeholder='Select view']")
            if views:
                print("         - Chọn View (Room Mới)...")
                self.handle_combobox(views[-1], "o", "View")

            # 5. Bed Type (Room Mới - lấy cái cuối cùng [-1])
            beds = self.driver.find_elements(By.XPATH, "//input[@placeholder='Select bed type']")
            if beds:
                print("         - Chọn Bed Type (gõ 'p')...")
                self.handle_combobox(beds[-1], "p", "Bed Type")

            # 6. Max Occupancy & Adult/Child
            adults = self.driver.find_elements(By.XPATH, "//input[contains(@name, 'adults')]")
            if adults:
                last_adult = adults[-1]
                self.enter_text_element(last_adult, adult)
                
                children = self.driver.find_elements(By.XPATH, "//input[contains(@name, 'children')]")
                if children: self.enter_text_element(children[-1], child)

                # Max Occupancy
                try:
                    max_occ_input = last_adult.find_element(By.XPATH, "./preceding::input[@role='combobox'][1]")
                    self.scroll_to_element(max_occ_input)
                    self.force_click(max_occ_input)
                    time.sleep(0.5)
                    max_occ_input.send_keys(max_occ)
                    time.sleep(0.5)
                    max_occ_input.send_keys(Keys.ENTER)
                except:
                    print("      ! Lỗi nhập Max Occupancy")

        except Exception as e:
            print(f"      ! Lỗi nhập phòng mới: {e}")

    def get_toast_message(self):
        try:
            return self.wait.until(lambda d: d.find_element(By.CLASS_NAME, "ant-message-notice")).text
        except:
            return None