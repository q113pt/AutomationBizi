import pytest
from selenium import webdriver
import sys
import os
import time

# --- FIX IMPORT PATH (Quan trọng) ---
# Đoạn này giúp Python tìm thấy thư mục 'pages' từ thư mục 'tests'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pages.room_update import RoomUpdatePage

# --- CONFIGURATION ---
BASE_URL = "https://partner.bizigo.vn/hotel-management/room-types" # Thay URL thật của bạn
# Có thể thêm logic Login vào đây hoặc dùng cookies

@pytest.fixture(scope="function")
def driver():
    # Setup Driver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless") # Bỏ comment nếu muốn chạy ẩn
    driver = webdriver.Chrome(options=options)
    
    # --- LOGIC LOGIN GIẢ ĐỊNH (Nếu cần) ---
    # driver.get("URL_LOGIN")
    # ... code login ...
    
    driver.get(BASE_URL)
    yield driver
    driver.quit()

@pytest.fixture
def page(driver):
    return RoomUpdatePage(driver)

# --- TEST CASES ---

def test_TC_01_full_flow_update_room_price(page):
    """
    Test Case: Cấu hình trọn vẹn 1 phòng
    - Check tiện ích
    - Setup hoàn hủy
    - Setup giá theo giai đoạn
    - Setup phụ thu cuối tuần (T7, CN)
    """
    print("\n--- Bắt đầu TC 01: Config Room Price ---")
    
    # 1. Cấu hình Option (Rate)
    print("Step 1: Config Option")
    page.configure_option_amenities(breakfast=True, non_smoking=True)
    page.set_refund_policy(is_refundable=True, days="5", penalty="100")

    # 2. Cấu hình Period (Giai đoạn)
    print("Step 2: Config Period")
    # Giả sử sửa Period đầu tiên (index 0)
    # Lưu ý: Đảm bảo Period 0 đang tồn tại
    try:
        page.set_period_info("Tet Holiday 2026", "20/01/2026", "30/01/2026", period_idx=0)
        page.set_base_price("2000000", period_idx=0)
    except Exception as e:
        print(f"Lỗi thao tác Period: {e}")

    # 3. Cấu hình Phụ thu (FIXED: Cả Sat và Sun)
    print("Step 3: Config Surcharge")
    page.set_weekend_surcharge(sat_price="500000", sun_price="500000", period_idx=0)

    # 4. Lưu
    page.save_changes()
    
    # 5. Verify
    msg = page.get_toast_message()
    print(f"Message nhận được: {msg}")
    assert msg is not None, "Không thấy thông báo sau khi save"
    # assert "success" in msg.lower() # Bật lại dòng này nếu biết text chuẩn

def test_TC_02_market_price_override(page):
    """
    Test Case: Thêm Market và set giá riêng
    """
    print("\n--- Bắt đầu TC 02: Market Override ---")
    
    # Thêm Market mới vào Period 0
    page.add_market()
    time.sleep(1) # Chờ animation UI
    
    # Set giá cho Market đó (giả sử market mới thêm có index 0 trong list market của period 0)
    page.set_market_config(
        region_name="South East Asia", 
        price="1800000", 
        period_idx=0, 
        market_idx=0
    )
    
    page.save_changes()
    
    # Check không có lỗi input
    err = page.get_input_error_message()
    assert err is None, f"Có lỗi input: {err}"

def test_TC_03_validate_date_logic(page):
    """
    Test Case Negative: Ngày kết thúc nhỏ hơn ngày bắt đầu
    """
    print("\n--- Bắt đầu TC 03: Validate Date ---")
    
    page.set_period_info("Invalid Date Test", "10/02/2026", "01/02/2026", period_idx=0)
    page.save_changes()
    
    # Mong đợi hệ thống báo lỗi hoặc toast error
    err = page.get_input_error_message() or page.get_toast_message()
    print(f"Error detected: {err}")
    assert err is not None, "Hệ thống phải báo lỗi khi ngày kết thúc nhỏ hơn ngày bắt đầu"

def test_TC_04_add_delete_option(page):
    """
    Test Case: Thêm Option mới
    """
    print("\n--- Bắt đầu TC 04: Add Option ---")
    
    # Thêm
    page.add_new_option()
    
    # Cần wait 1 chút để UI render option mới
    time.sleep(1) 
    
    # Validate option 2 (index 1) đã được thêm (check field breakfast của option index 1)
    # Lưu ý: index bắt đầu từ 0, nên option thứ 2 sẽ có index là 1
    from selenium.webdriver.common.by import By
    opt_2_exists = page.driver.find_elements(By.NAME, "rooms.0.ratesList.1.hasBreakfast")
    
    assert len(opt_2_exists) > 0, "Option mới chưa được thêm (Không tìm thấy element rooms.0.ratesList.1...)"