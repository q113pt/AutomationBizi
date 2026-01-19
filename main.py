import time
import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys # <--- Bắt buộc có dòng này
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CẤU HÌNH ---
current_folder = os.path.dirname(os.path.abspath(__file__))
driver_path = os.path.join(current_folder, "msedgedriver.exe")
user_data_dir = os.path.join(current_folder, "User_Data")

options = Options()
options.add_argument(f"user-data-dir={user_data_dir}")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

service = EdgeService(executable_path=driver_path)
driver = webdriver.Edge(service=service, options=options)
wait = WebDriverWait(driver, 10)

try:
    print("1. Đang truy cập trang web...")
    driver.get("https://qa-tms.bizihub.vn/dashboard/room-inventory-management")
    driver.maximize_window()

    # --- LOGIC ĐĂNG NHẬP "SIÊU SẠCH" ---
    try:
        # Kiểm tra xem có ô username không
        user_field = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.NAME, "username"))
        )
        print("-> Phát hiện màn hình Đăng nhập. Đang login...")

        # --- BƯỚC 1: Xử lý Username (Dùng Ctrl+A -> Delete) ---
        user_field.click()
        time.sleep(0.5)
        # Thay vì .clear(), ta dùng combo phím:
        user_field.send_keys(Keys.CONTROL + "a") # Chọn tất cả chữ đang có
        user_field.send_keys(Keys.DELETE)        # Xóa sạch sành sanh
        time.sleep(0.5)                          # Chờ 1 nhịp cho React hiểu là ô đã trống
        user_field.send_keys("tmssuperadmin")    # Điền mới
        
        # --- BƯỚC 2: Xử lý Password (Dùng Ctrl+A -> Delete) ---
        pass_field = driver.find_element(By.NAME, "password")
        pass_field.click()
        time.sleep(0.5)
        # Xóa sạch password cũ/autofill
        pass_field.send_keys(Keys.CONTROL + "a")
        pass_field.send_keys(Keys.DELETE)
        time.sleep(0.5) 
        pass_field.send_keys("tmssuperadmin123")
        
        # --- BƯỚC 3: Bấm nút ---
        print("-> Đang tìm nút Đăng nhập...")
        try:
            login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_btn.click()
        except:
            login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Đăng nhập')]")
            login_btn.click()

    except Exception as login_error:
        print(f"-> Thông báo (Bỏ qua nếu đã vào trong): {login_error}")

    # --- KIỂM TRA KẾT QUẢ ---
    print("-> Đang chờ vào Dashboard...")
    wait.until(EC.url_contains("dashboard"))
    print("SUCCESS: Đăng nhập thành công! Script không bị duplicate nữa.")

    time.sleep(5)

except Exception as e:
    print(f"LỖI: {e}")
    driver.save_screenshot("loi_cuoi_cung.png") 

finally:
    driver.quit()