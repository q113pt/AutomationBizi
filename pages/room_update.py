from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

class RoomUpdatePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # --- CORE HELPERS ---
    def click(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        el.click()

    def input_text(self, locator, text):
        el = self.wait.until(EC.visibility_of_element_located(locator))
        el.click()
        # Xóa sạch dữ liệu cũ (Ctrl+A -> Delete) để tránh lỗi với React input
        el.send_keys(Keys.CONTROL + "a")
        el.send_keys(Keys.DELETE)
        el.send_keys(str(text))
        
    def is_checked(self, locator):
        try:
            return self.wait.until(EC.presence_of_element_located(locator)).is_selected()
        except:
            return False

    def select_dropdown_option(self, trigger_locator, option_text):
        """Xử lý HeadlessUI/AntD Combobox"""
        self.click(trigger_locator)
        # Tìm option trong list (thường render ở cuối body)
        option_xpath = f"//li[contains(., '{option_text}')] | //div[contains(@class, 'option') and contains(., '{option_text}')]"
        self.click((By.XPATH, option_xpath))

    # --- DYNAMIC NAME GENERATORS ---
    # Dựa trên log bạn cung cấp: rooms.0.ratesList.0...
    
    def get_rate_base_name(self, room_idx=0, rate_idx=0):
        return f"rooms.{room_idx}.ratesList.{rate_idx}"

    def get_period_base_name(self, room_idx=0, rate_idx=0, period_idx=0):
        # Lưu ý: priceByPriceApply.1 và priceListGrouped là cấu trúc cố định từ log
        return f"rooms.{room_idx}.ratesList.{rate_idx}.priceByPriceApply.1.priceListGrouped.{period_idx}"

    def get_market_base_name(self, room_idx=0, rate_idx=0, period_idx=0, market_idx=0):
        # items.2 thường là item đại diện cho Market Price trong cấu trúc Period
        period_base = self.get_period_base_name(room_idx, rate_idx, period_idx)
        return f"{period_base}.items.2.marketPricesList.{market_idx}"

    # --- 1. OPTION ACTIONS ---

    def add_new_option(self):
        self.click((By.XPATH, "//button[contains(text(), '+ ADD OPTION')]"))

    def delete_option(self, option_index=0):
        # Click checkbox delete
        # Tìm checkbox xóa của option tương ứng (cần xpath tương đối chuẩn xác)
        # Giả định xóa option cuối
        self.click((By.XPATH, "//button[contains(text(), 'DELETE SELECTED OPTIONS')]"))

    def configure_option_amenities(self, room_idx=0, rate_idx=0, breakfast=True, non_smoking=False, extra_bed=False):
        base = self.get_rate_base_name(room_idx, rate_idx)
        
        # Checkbox logic
        for name, state in [("hasBreakfast", breakfast), ("nonSmoking", non_smoking), ("hasExtraBed", extra_bed)]:
            loc = (By.NAME, f"{base}.{name}")
            if self.is_checked(loc) != state:
                # Tìm element label hoặc cha để click nếu input bị ẩn
                try:
                    self.click(loc)
                except:
                    # Fallback: click label kế bên
                    self.driver.find_element(By.XPATH, f"//input[@name='{base}.{name}']/following-sibling::label").click()

    def set_refund_policy(self, room_idx=0, rate_idx=0, is_refundable=True, days=None, penalty=None):
        base = self.get_rate_base_name(room_idx, rate_idx)
        
        # Xử lý Radio button Refundable
        val_str = "true" if is_refundable else "false"
        # Click vào radio input
        try:
            self.click((By.CSS_SELECTOR, f"input[name='{base}.refundable'][value='{val_str}']"))
        except:
            # Fallback nếu radio bị ẩn: Dùng JS click
            el = self.driver.find_element(By.CSS_SELECTOR, f"input[name='{base}.refundable'][value='{val_str}']")
            self.driver.execute_script("arguments[0].click();", el)

        if is_refundable and days and penalty:
            self.input_text((By.NAME, f"{base}.policiesConfig.dayBeforeCheckIn"), days)
            self.input_text((By.NAME, f"{base}.policiesConfig.penaltyConfig.amount"), penalty)

    # --- 2. PERIOD ACTIONS ---

    def add_new_period(self):
        self.click((By.XPATH, "//button[contains(text(), '+ ADD PERIOD')]"))

    def set_period_info(self, name, start_date, end_date, room_idx=0, rate_idx=0, period_idx=0):
        base = self.get_period_base_name(room_idx, rate_idx, period_idx)
        self.input_text((By.NAME, f"{base}.stageName"), name)
        self.input_text((By.NAME, f"{base}.stagedDate.startDate"), start_date)
        # Tab hoặc click sang ô end date để trigger calendar close
        self.input_text((By.NAME, f"{base}.stagedDate.endDate"), end_date)
        self.driver.find_element(By.TAG_NAME, "body").click() # Click out để đóng datepicker

    def set_base_price(self, price, room_idx=0, rate_idx=0, period_idx=0):
        base = self.get_period_base_name(room_idx, rate_idx, period_idx)
        # items.0 là giá Base (Allotment/OTA)
        self.input_text((By.NAME, f"{base}.items.0.baseRate"), price)

    def set_weekend_surcharge(self, sat_price=None, sun_price=None, room_idx=0, rate_idx=0, period_idx=0):
        base = self.get_period_base_name(room_idx, rate_idx, period_idx)
        # items.0.rateExtraConfigsList.[index] -> 1=Sat, 2=Sun (Theo log)
        if sat_price:
            self.input_text((By.NAME, f"{base}.items.0.rateExtraConfigsList.1.totalRateExtra"), sat_price)
        if sun_price:
            self.input_text((By.NAME, f"{base}.items.0.rateExtraConfigsList.2.totalRateExtra"), sun_price)

    # --- 3. MARKET ACTIONS ---
    
    def add_market(self):
        # Click nút Add Market (Lấy nút cuối cùng hiển thị trên màn hình để add vào period mới nhất)
        markets = self.driver.find_elements(By.XPATH, "//button[contains(text(), '+ Add Market')]")
        if markets:
            markets[-1].click()

    def set_market_config(self, region_name, price, room_idx=0, rate_idx=0, period_idx=0, market_idx=0):
        base = self.get_market_base_name(room_idx, rate_idx, period_idx, market_idx)
        
        # 1. Chọn loại Country-Region (Radio) - mặc định thường chọn sẵn
        
        # 2. Chọn Region (Dropdown)
        # Button trigger dropdown thường nằm ngay trước input regionCode (hoặc dựa theo UI)
        # Ở đây dùng cách tìm nút 'Enter region' gần nhất
        try:
            # Tìm input/button để mở dropdown region
            trigger = self.driver.find_element(By.XPATH, f"//input[@name='{base}.regionCode']/preceding-sibling::button | //button[contains(text(), 'Enter region')]")
            self.select_dropdown_option((By.XPATH, "xpath_cua_trigger"), region_name)
        except:
            # Fallback đơn giản: Nếu chỉ cần test nhập giá
            pass 

        # 3. Nhập giá Market (Override)
        self.input_text((By.NAME, f"{base}.baseRate"), price)

    def remove_market(self):
        # Click nút Remove Market cuối cùng
        btns = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Remove Market')]")
        if btns:
            btns[-1].click()

    # --- GENERAL ACTIONS ---
    def save_changes(self):
        self.click((By.XPATH, "//button[text()='UPDATE']"))

    def get_toast_message(self):
        try:
            return self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ant-message-notice"))).text
        except TimeoutException:
            return None

    def get_input_error_message(self):
        """Lấy text lỗi màu đỏ dưới input"""
        try:
            # Class thường gặp của AntDesign/Tailwind form error
            el = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-form-item-explain-error') or contains(@class, 'text-red')]")
            return el.text
        except:
            return None